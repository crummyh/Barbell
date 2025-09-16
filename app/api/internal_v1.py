from typing import Annotated
from uuid import UUID

from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    HTTPException,
    Security,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlmodel import Session, asc, select
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from app.api.public_v1 import request_download_batch, test_upload_archive
from app.core.dependencies import (
    RateLimiter,
    generate_api_key,
    minimum_role,
    rate_limit_config,
    require_login,
    require_role,
)
from app.crud import image, label_category, user
from app.database import get_session
from app.models.download_batch import (
    DownloadBatch,
    DownloadBatchCreate,
    DownloadBatchPublic,
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
    image_response,
)
from app.models.upload_batch import UploadBatch, UploadBatchPublic
from app.models.user import User, UserPublic, UserRole, UserUpdate
from app.services import buckets

subapp = FastAPI()
origins = ["http://127.0.0.1:8000", "https://127.0.0.1:8000"]
subapp.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@subapp.get(
    "/image", dependencies=[Depends(RateLimiter(requests_limit=5, time_window=5))]
)
def get_image_for_review(
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))],
    session: Annotated[Session, Depends(get_session)],
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

    return db_image.get_public()


@subapp.put(
    "/image/update",
    dependencies=[Depends(RateLimiter(requests_limit=5, time_window=5))],
)
def update_image(
    id: UUID,
    image_update: ImageUpdate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))],
    remove_image: bool = False,
) -> ImagePublic | None:
    if remove_image:
        image.delete(session, id)
        return

    db_image = image.get(session, id)
    if not db_image:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Image not found")

    try:
        image.update(session, id, image_update)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return db_image.get_public()


@subapp.get(
    "/image/{image_id}",
    dependencies=[Depends(RateLimiter(requests_limit=5, time_window=5))],
)
def get_image_by_id(
    image_id: UUID,
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))],
) -> StreamingResponse:
    return image_response(buckets.get_image(image_id))


@subapp.post(
    "/token", dependencies=[Depends(RateLimiter(requests_limit=10, time_window=5))]
)
def redirect_token():
    """
    Redirects requests from here to the main auth router
    """
    return RedirectResponse(url="/token", status_code=307)


@subapp.put(
    "/user/update", dependencies=[Depends(RateLimiter(requests_limit=5, time_window=5))]
)
def update_user(
    username: str,
    user_update: UserUpdate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Security(require_role(UserRole.ADMIN))],
) -> UserPublic:
    db_user = user.get_user_from_username(session, username)
    if db_user is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")

    try:
        user.update(session, db_user.id, user_update)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return db_user.get_public()


@subapp.post("/categories/super/create")
def create_label_super_category(
    category: LabelSuperCategoryCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))],
) -> LabelSuperCategoryPublic:
    try:
        return label_category.create_super(session, category).get_public()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@subapp.get("/categories/super")
def get_label_super_categories(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Security(require_login)],
) -> list[LabelSuperCategoryPublic]:
    return [i.get_public() for i in session.exec(select(LabelSuperCategory)).all()]


@subapp.put("/categories/super/update")
def modify_label_super_category(
    id: int,
    update: LabelSuperCategoryUpdate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))],
) -> LabelSuperCategoryPublic:
    try:
        public_label = label_category.update_super(session, id, update)
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    if public_label is None:
        raise HTTPException(status_code=404, detail="Super Category not found")
    return public_label.get_public()


@subapp.delete("/categories/super/remove")
def remove_label_super_category(
    id: int,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))],
):
    try:
        if label_category.delete_super(session, id) is True:
            return {"detail": "Successfully deleted"}
        else:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="Catagory does not exist"
            )
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@subapp.post("/categories/create")
def create_label_category(
    category: LabelCategoryCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))],
) -> LabelCategoryPublic:
    try:
        return label_category.create(session, category).get_public()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@subapp.delete("/categories/remove")
def remove_label_category(
    id: int,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))],
):
    try:
        if label_category.delete(session, id) is True:
            return {"detail": "Successfully deleted"}
        else:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="Catagory does not exist"
            )
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@subapp.put("/categories/update")
def modify_label_category(
    id: int,
    update: LabelCategoryUpdate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))],
) -> LabelCategoryPublic:
    try:
        public_label = label_category.update(session, id, update)
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    if public_label is None:
        raise HTTPException(status_code=404, detail="Super Category not found")
    return public_label.get_public()


@subapp.get("/download-batches/history")
def get_download_batch_history(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Security(require_login)],
) -> list[DownloadBatchPublic] | None:
    batches = session.exec(
        select(DownloadBatch).where(DownloadBatch.user == current_user.id)
    ).all()
    if len(batches) == 0:
        return None

    return [i.get_public() for i in batches]


@subapp.get("/upload-batches/history")
def get_upload_batch_history(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Security(require_login)],
) -> list[UploadBatchPublic] | None:
    batches = session.exec(
        select(UploadBatch).where(UploadBatch.user == current_user.id)
    ).all()
    if len(batches) == 0:
        return None

    return [i.get_public() for i in batches]


@subapp.put("/api-key")
def create_or_rotate_api_key(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Security(require_login)],
):
    try:
        current_user.api_key = generate_api_key()
        return current_user.api_key
    except Exception:
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to change API key")


@subapp.get("/api-key")
def get_api_key(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Security(require_login)],
) -> str | None:
    return current_user.api_key


@subapp.put("/download")
def download_redirect(
    request: DownloadBatchCreate,
    background_tasks: BackgroundTasks,
    user: Annotated[User, Depends(require_login)],
    session: Annotated[Session, Depends(get_session)],
):
    request_download_batch(request, background_tasks, user, session)


@subapp.post("/admin/rate-limit/update")
def update_rate_limit(
    cfg: RateLimitUpdate, user: Annotated[User, Depends(minimum_role(UserRole.ADMIN))]
) -> dict:
    rate_limit_config[cfg.route]["requests_limit"] = cfg.requests_limit
    rate_limit_config[cfg.route]["time_window"] = cfg.time_window
    return {"message": "Rate limit updated", "config": rate_limit_config}


@subapp.get("/admin/rate-limit")
def get_rate_limit(user: Annotated[User, Depends(minimum_role(UserRole.ADMIN))]):
    return rate_limit_config


@subapp.post("/upload/test")
async def test_upload(
    archive: UploadFile,
    hash: str,
    user: Annotated[User, Depends(require_login)],
):
    await test_upload_archive(archive, hash, user)
