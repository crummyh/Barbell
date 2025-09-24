import tarfile
from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Security,
    UploadFile,
)
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlmodel import asc, select
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from app.core import config
from app.core.dependencies import (
    RateLimiter,
    SessionDep,
    generate_api_key,
    get_current_user,
    get_password_hash,
    minimum_role,
    rate_limit_config,
    require_role,
)
from app.core.helpers import (
    get_hash_with_streaming,
)
from app.crud import download_batch, image, label_category, upload_batch, user
from app.models.download_batch import (
    DownloadBatchCreate,
    DownloadBatchPublic,
    DownloadStatus,
)
from app.models.image import Image, ImagePublic, ImageReviewStatus, ImageUpdate
from app.models.label_category import (
    LabelCategoryCreate,
    LabelCategoryPublic,
    LabelCategoryUpdate,
    LabelSuperCategory,
    LabelSuperCategoryCreate,
    LabelSuperCategoryPublic,
    LabelSuperCategoryUpdate,
)
from app.models.models import (
    RateLimitUpdate,
    StatsOut,
    image_response,
)
from app.models.team import Team
from app.models.upload_batch import (
    UploadBatchCreate,
    UploadBatchPublic,
)
from app.models.user import User, UserPublic, UserRole, UserUpdate
from app.services import buckets
from app.services.buckets import create_upload_batch, get_download_batch
from app.services.monitoring import get_uptime
from app.tasks.download_packaging import create_download_batch
from app.tasks.image_processing import (
    estimate_upload_processing_time,
    process_batch_async,
    validate_image_pre,
)

router = APIRouter()


@router.get("/ping", tags=["Stats"])
async def ping() -> dict[str, str]:
    return {"ping": "pong!"}


@router.get(
    "/stats",
    tags=["Stats"],
    dependencies=[Depends(RateLimiter(requests_limit=20, time_window=10))],
)
def get_stats(session: SessionDep) -> StatsOut:
    """
    Get stats about the entire database
    """
    out = StatsOut(
        image_count=session.exec(
            select(func.count())
            .select_from(Image)
            .where(Image.review_status == ImageReviewStatus.APPROVED)
        ).one(),
        un_reviewed_image_count=session.exec(
            select(func.count())
            .select_from(Image)
            .where(Image.review_status != ImageReviewStatus.APPROVED)
        ).one(),
        team_count=session.exec(select(func.count()).select_from(Team)).one(),
        uptime=get_uptime(),
    )
    return out


@router.get("/stats/labels", tags=["Stats"])
def get_label_info(
    session: SessionDep,
) -> list[LabelSuperCategoryPublic]:
    categories = session.exec(select(LabelSuperCategory)).all()

    if not categories:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="No categories found"
        )

    output = []
    for catagory in categories:
        public = catagory.get_public()
        output.append(public)

    return output


@router.get(
    "/upload/status/{batch_id}",
    tags=["Upload"],
    dependencies=[Depends(RateLimiter(requests_limit=30, time_window=10))],
)
def get_upload_batch_status(
    batch_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
) -> UploadBatchPublic:
    batch = upload_batch.get(session, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    out = batch.get_public()
    out.estimated_time_left = estimate_upload_processing_time(session, batch_id)

    return out


@router.post("/upload/test", tags=["Upload"])
async def check_upload_archive(
    archive: UploadFile, hash: str, user: Annotated[User, Depends(get_current_user)]
) -> dict[str, str]:
    if not tarfile.is_tarfile(archive.file):
        raise HTTPException(status_code=415, detail="File must be of type .tar.gz")

    if archive.size and (archive.size > config.MAX_FILE_SIZE):
        raise HTTPException(
            status_code=413,
            detail=f"File is too large. Max size: {config.MAX_FILE_SIZE / (1024**3):.1f}GB",
        )

    if get_hash_with_streaming(archive.file, config.BUCKET_NAME_HASH_ALGORITHM) != hash:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is corrupted (hash mismatch) (Are you using sha256?)",
        )

    archive.file.seek(0)
    with tarfile.open(fileobj=archive.file, mode="r:gz") as tar:
        image_files = [m for m in tar.getmembers() if m.isfile()]

        if len(image_files) == 0:
            raise HTTPException(
                status_code=400, detail="Archive is empty. Are the images in root?"
            )

        for i in image_files:
            if not validate_image_pre(i):
                raise HTTPException(
                    status_code=400,
                    detail=f'Image "{i.name}" is not a supported file type. See `PIL.Image.registered_extensions().items()`',
                )

    return {"status": "success"}


@router.post(
    "/upload",
    tags=["Upload"],
    dependencies=[Depends(RateLimiter(requests_limit=2, time_window=60))],
)
async def upload(
    archive: UploadFile,
    hash: str,
    background_tasks: BackgroundTasks,
    user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
    capture_time: datetime = datetime.now(timezone.utc),
) -> UploadBatchPublic:
    """
    Upload images to the dataset. Requires an API key

    `archive`: The images in a .tar.gz archive

    `hash`: A ***sha256*** hash of the archive

    `capture_time`: The rough time that the data was gathered
    """

    await check_upload_archive(archive, hash, user)

    try:
        assert user.id
        assert archive.size

        batch = upload_batch.create(
            session,
            UploadBatchCreate(
                capture_time=capture_time,
                file_size=archive.size,
                user_id=user.id,
            ),
        )
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail="There was an error adding the batch to the database. Sorry!",
        ) from None

    assert batch.id
    create_upload_batch(archive.file, batch.id)

    background_tasks.add_task(process_batch_async, batch_id=batch.id)

    out = batch.get_public()
    out.estimated_time_left = config.DEFAULT_PROCESSING_TIME
    return out


@router.get(
    "/download/status/{batch_id}",
    tags=["Download"],
    dependencies=[Depends(RateLimiter(requests_limit=30, time_window=10))],
)
def get_download_batch_status(
    batch_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
) -> DownloadBatchPublic:
    batch = download_batch.get(session, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    out = batch.get_public()
    return out


@router.put(
    "/download/request",
    tags=["Download"],
    dependencies=[Depends(RateLimiter(requests_limit=2, time_window=60))],
)
def request_download_batch(
    request: DownloadBatchCreate,
    background_tasks: BackgroundTasks,
    user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
) -> DownloadBatchPublic:
    try:
        batch = download_batch.create(session, request, user)

    except Exception:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add batch to database",
        ) from None

    background_tasks.add_task(create_download_batch, batch_id=batch.id)
    return batch.get_public()


@router.put(
    "/download/get/{batch_id}",
    tags=["Download"],
    dependencies=[Depends(RateLimiter(requests_limit=2, time_window=60))],
)
def download_download_batch(
    batch_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
) -> StreamingResponse:
    batch = download_batch.get(session, batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")

    if batch.status != DownloadStatus.READY:
        raise HTTPException(status_code=400, detail="Batch is not ready to download")

    return StreamingResponse(
        content=get_download_batch(batch_id),
        media_type="application/gzip",
        headers={"Content-Disposition": "attachment; filename=images.tar.gz"},
    )


@router.put(
    "/rotate-key",
    tags=["Management"],
    dependencies=[Depends(RateLimiter(requests_limit=1, time_window=60))],
)
def rotate_api_key(
    user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
) -> str:
    key = generate_api_key()
    user.api_key = get_password_hash(key)
    session.add(user)
    session.commit()

    return key


@router.get(
    "/image", dependencies=[Depends(RateLimiter(requests_limit=5, time_window=5))]
)
def get_image_for_review(
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))],
    session: SessionDep,
    target_status: ImageReviewStatus,
) -> ImagePublic:
    statement = (
        select(Image)
        .where(Image.review_status == target_status)
        .order_by(asc(Image.created_at))
        .limit(1)
    )
    db_image = session.exec(statement).one()
    if not db_image:
        raise HTTPException(status_code=500, detail="No images found")

    public_image: ImagePublic = db_image.get_public()
    return public_image


@router.put(
    "/image/update",
    dependencies=[Depends(RateLimiter(requests_limit=5, time_window=5))],
)
def update_image(
    id: UUID,
    image_update: ImageUpdate,
    session: SessionDep,
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))],
    remove_image: bool = False,
) -> ImagePublic | None:
    if remove_image:
        image.delete(session, id)
        return None

    db_image = image.get(session, id)
    if not db_image:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Image not found")

    try:
        image.update(session, id, image_update)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from None
    else:
        return db_image.get_public()


@router.get(
    "/image/{image_id}",
    dependencies=[Depends(RateLimiter(requests_limit=5, time_window=5))],
)
def get_image_by_id(
    image_id: UUID,
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))],
) -> StreamingResponse:
    return image_response(buckets.get_image(image_id))


@router.put(
    "/user/update", dependencies=[Depends(RateLimiter(requests_limit=5, time_window=5))]
)
def update_user(
    username: str,
    user_update: UserUpdate,
    session: SessionDep,
    current_user: Annotated[User, Security(require_role(UserRole.ADMIN))],
) -> UserPublic:
    db_user = user.get_user_from_username(session, username)
    if db_user is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")

    try:
        assert db_user.id
        user.update(session, db_user.id, user_update)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from None
    else:
        return db_user.get_public()


@router.post("/categories/super/create")
def create_label_super_category(
    category: LabelSuperCategoryCreate,
    session: SessionDep,
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))],
) -> LabelSuperCategoryPublic:
    try:
        return label_category.create_super(session, category).get_public()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from None


@router.get("/categories/super")
def get_label_super_categories(
    session: SessionDep,
    current_user: Annotated[User, Security(get_current_user)],
) -> list[LabelSuperCategoryPublic]:
    return [i.get_public() for i in session.exec(select(LabelSuperCategory)).all()]


@router.put("/categories/super/update")
def modify_label_super_category(
    id: int,
    update: LabelSuperCategoryUpdate,
    session: SessionDep,
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))],
) -> LabelSuperCategoryPublic:
    try:
        public_label = label_category.update_super(session, id, update)
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e)) from None
    if public_label is None:
        raise HTTPException(status_code=404, detail="Super Category not found")
    return public_label.get_public()


@router.delete("/categories/super/remove")
def remove_label_super_category(
    id: int,
    session: SessionDep,
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))],
) -> dict[str, str]:
    try:
        if label_category.delete_super(session, id) is True:
            return {"detail": "Successfully deleted"}
        else:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="Catagory does not exist"
            )
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e)) from None


@router.post("/categories/create")
def create_label_category(
    category: LabelCategoryCreate,
    session: SessionDep,
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))],
) -> LabelCategoryPublic:
    try:
        new_cat = label_category.create(session, category).get_public()
        assert isinstance(new_cat, LabelCategoryPublic)
        return new_cat
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from None


@router.delete("/categories/remove")
def remove_label_category(
    id: int,
    session: SessionDep,
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))],
) -> dict[str, str]:
    try:
        if label_category.delete(session, id) is True:
            return {"detail": "Successfully deleted"}
        else:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="Catagory does not exist"
            )
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e)) from None


@router.put("/categories/update")
def modify_label_category(
    id: int,
    update: LabelCategoryUpdate,
    session: SessionDep,
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))],
) -> LabelCategoryPublic:
    try:
        public_label = label_category.update(session, id, update)
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e)) from None
    if public_label is None:
        raise HTTPException(status_code=404, detail="Super Category not found")
    return public_label.get_public()


@router.get("/download-batches/history")
def get_download_batch_history(
    session: SessionDep,
    current_user: Annotated[User, Security(get_current_user)],
) -> list[DownloadBatchPublic] | None:
    batches = current_user.download_batches
    if len(batches) == 0:
        return None

    return [i.get_public() for i in batches]


@router.get("/upload-batches/history")
def get_upload_batch_history(
    session: SessionDep,
    current_user: Annotated[User, Security(get_current_user)],
) -> list[UploadBatchPublic] | None:
    batches = current_user.upload_batches
    if len(batches) == 0:
        return None

    return [i.get_public() for i in batches]


@router.put("/api-key")
def create_or_rotate_api_key(
    session: SessionDep,
    current_user: Annotated[User, Security(get_current_user)],
) -> str:
    try:
        current_user.api_key = generate_api_key()
        return current_user.api_key
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to change API key"
        ) from None


@router.post("/admin/rate-limit/update")
def update_rate_limit(
    cfg: RateLimitUpdate, user: Annotated[User, Depends(minimum_role(UserRole.ADMIN))]
) -> dict:
    rate_limit_config[cfg.route]["requests_limit"] = cfg.requests_limit
    rate_limit_config[cfg.route]["time_window"] = cfg.time_window
    return {"message": "Rate limit updated", "config": rate_limit_config}


@router.get("/admin/rate-limit")
def get_rate_limit(
    user: Annotated[User, Depends(minimum_role(UserRole.ADMIN))],
) -> dict:
    return rate_limit_config
