import tarfile
from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile
from fastapi.exceptions import HTTPException
from sqlalchemy import func
from sqlmodel import Session, select
from starlette.responses import StreamingResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.core import config
from app.core.dependencies import (
    RateLimiter,
    generate_api_key,
    get_password_hash,
    handle_api_key,
)
from app.core.helpers import (
    get_hash_with_streaming,
)
from app.crud import download_batch, upload_batch
from app.database import get_session
from app.models.download_batch import (
    DownloadBatchCreate,
    DownloadBatchPublic,
    DownloadStatus,
)
from app.models.image import Image, ImageReviewStatus
from app.models.label_category import (
    LabelSuperCategory,
    LabelSuperCategoryPublic,
)
from app.models.models import (
    StatsOut,
)
from app.models.team import Team
from app.models.upload_batch import (
    UploadBatchCreate,
    UploadBatchPublic,
)
from app.models.user import User
from app.services.buckets import create_upload_batch, get_download_batch
from app.services.monitoring import get_uptime
from app.tasks.download_packaging import create_download_batch
from app.tasks.image_processing import (
    estimate_upload_processing_time,
    process_batch_async,
    validate_image_pre,
)

router = APIRouter()

# ========== { Public API } ========== #


@router.get("/ping", tags=["Stats"])
async def ping() -> dict[str, str]:
    return {"ping": "pong!"}


@router.get(
    "/stats",
    tags=["Stats"],
    dependencies=[Depends(RateLimiter(requests_limit=20, time_window=10))],
)
def get_stats(session: Annotated[Session, Depends(get_session)]) -> StatsOut:
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
    session: Annotated[Session, Depends(get_session)],
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


# ========== { Auth API } ========== #


@router.get(
    "/upload/status/{batch_id}",
    tags=["Upload"],
    dependencies=[Depends(RateLimiter(requests_limit=30, time_window=10))],
)
def get_upload_batch_status(
    batch_id: UUID,
    user: Annotated[User, Depends(handle_api_key)],
    session: Annotated[Session, Depends(get_session)],
) -> UploadBatchPublic:
    batch = upload_batch.get(session, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    out = batch.get_public()
    out.estimated_time_left = estimate_upload_processing_time(session, batch_id)

    return out


@router.post("/upload/test", tags=["Upload"])
async def check_upload_archive(
    archive: UploadFile, hash: str, user: Annotated[User, Depends(handle_api_key)]
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
    user: Annotated[User, Depends(handle_api_key)],
    session: Annotated[Session, Depends(get_session)],
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
    user: Annotated[User, Depends(handle_api_key)],
    session: Annotated[Session, Depends(get_session)],
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
    user: Annotated[User, Depends(handle_api_key)],
    session: Annotated[Session, Depends(get_session)],
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
    user: Annotated[User, Depends(handle_api_key)],
    session: Annotated[Session, Depends(get_session)],
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


# ==========={ Management }=========== #


@router.put(
    "/rotate-key",
    tags=["Management"],
    dependencies=[Depends(RateLimiter(requests_limit=1, time_window=60))],
)
def rotate_api_key(
    user: Annotated[User, Depends(handle_api_key)],
    session: Annotated[Session, Depends(get_session)],
) -> str:
    key = generate_api_key()
    user.api_key = get_password_hash(key)
    session.add(user)
    session.commit()

    return key
