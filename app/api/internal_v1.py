
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
from fastapi.responses import RedirectResponse
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
from app.crud import image
from app.database import get_session
from app.models.models import (
    Image,
    ImagePublic,
    ImageReviewStatus,
    ImageUpdate,
    RateLimitUpdate,
    User,
    UserRole,
    image_response,
)
from app.services import buckets

subapp = FastAPI()
origins = [
    "http://127.0.0.1:8000",
    "https://127.0.0.1:8000"
]
subapp.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@subapp.get("/review-image", dependencies=[Depends(RateLimiter(requests_limit=5, time_window=5))])
def get_image_for_review(
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))],
    session: Annotated[Session, Depends(get_session)],
    target_status: ImageReviewStatus
) -> ImagePublic:

    statement = (
        select(Image).where(Image.review_status == target_status)
        .order_by(asc(Image.created_at))
        .limit(1)
    )
    db_image = session.exec(statement).one()
    if not db_image:
        raise HTTPException(
            status_code=500,
            detail="No images found"
        )

    return db_image.get_public()

@subapp.put("/review-image", dependencies=[Depends(RateLimiter(requests_limit=5, time_window=5))])
def update_image_review_status(
    id: UUID,
    image_update: ImageUpdate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))],
    remove_image: bool = False
):
    if remove_image:
        image.delete(session, id)
        return

    db_image = image.get(session, id)
    if not db_image:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    update_image(session, id, image_update)

    session.commit()

@subapp.get("/image/{image_id}", dependencies=[Depends(RateLimiter(requests_limit=5, time_window=5))])
def get_image_by_id(
    image_id: UUID,
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))]
):
    return image_response(buckets.get_image(image_id))

@subapp.post("/token", dependencies=[Depends(RateLimiter(requests_limit=10, time_window=5))])
def redirect_token():
    """
    Redirects requests from here to the main auth router
    """
    return RedirectResponse(url="/token", status_code=307)

@subapp.put("/change-user-role", dependencies=[Depends(RateLimiter(requests_limit=5, time_window=5))])
def change_user_role(
    username: str,
    new_role: UserRole,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Security(require_role(UserRole.ADMIN))]
):
    db_user = user.get_user_from_username(username, session)
    db_user.role = new_role
    session.add(db_user)
    session.commit()

@subapp.post("/categories/super/create")
def create_label_super_category(
    category: LabelSuperCategory,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))]
):
    session.add(category)
    session.commit()

@subapp.get("/categories/super")
def get_label_super_categories(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Security(require_login)]
):
    return session.exec(select(LabelSuperCategory)).all()


@subapp.post("/categories/create")
def create_label_category(
    category: LabelCategory,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))]
):
    session.add(category)
    session.commit()

@subapp.delete("/categories/remove")
def remove_label_category(
    id: int,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))]
):
    try:
        session.delete(session.get(LabelCategory, id))
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Catagory does not exist"
        )
    else:
        session.commit()

@subapp.delete("/categories/super/remove")
def remove_label_super_category(
    id: int,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))]
):
    try:
        super_catagory = session.get(LabelSuperCategory, id)
        assert super_catagory
        if super_catagory.sub_categories:
            for catagory in super_catagory.sub_categories:
                session.delete(catagory)
        session.delete(super_catagory)
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Catagory does not exist"
        )
    else:
        session.commit()

@subapp.put("/categories/super/modify")
def modify_label_super_category(
    id: int,
    new_name: str,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))]
):
    try:
        catagory = session.get(LabelSuperCategory, id)
        assert catagory
        catagory.name = new_name
        session.add(catagory)
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Catagory does not exist"
        )
    else:
        session.commit()

@subapp.put("/categories/modify")
def modify_label_category(
    id: int,
    new_name: str,
    new_super_cat: int,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))]
):
    try:
        catagory = session.get(LabelCategory, id)
        assert catagory
        if (new_super_cat != 0):
            catagory.super_catagory_id = new_super_cat
        catagory.name = new_name
        session.add(catagory)
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Catagory does not exist"
        )
    else:
        session.commit()

@subapp.get("/download-batches/history")
def get_download_batch_history(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Security(require_login)]
):
    batches = session.exec(select(DownloadBatch).where(DownloadBatch.user == current_user.id)).all()
    if len(batches) == 0:
        return None

    return batches

@subapp.get("/upload-batches/history")
def get_upload_batch_history(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Security(require_login)]
):
    batches = session.exec(select(UploadBatch).where(UploadBatch.user == current_user.id)).all()
    if len(batches) == 0:
        return None

    return batches

@subapp.put("/api-key")
def create_or_rotate_api_key(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Security(require_login)]
):
    try:
        current_user.api_key = generate_api_key()
        return current_user.api_key
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to change API key"
        )

@subapp.get("/api-key")
def get_api_key(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Security(require_login)]
):
    return current_user.api_key

@subapp.put("/download")
def download_redirect(
    request: DownloadRequest,
    background_tasks: BackgroundTasks,
    user: Annotated[User, Depends(require_login)],
    session: Annotated[Session, Depends(get_session)],
):
    request_download_batch(request, background_tasks, user, session)

@subapp.post("/admin/rate-limit")
def update_rate_limit(
    cfg: RateLimitUpdate,
    user: Annotated[User, Depends(minimum_role(UserRole.ADMIN))]
):
    rate_limit_config[cfg.route]["requests_limit"] = cfg.requests_limit
    rate_limit_config[cfg.route]["time_window"] = cfg.time_window
    return {"message": "Rate limit updated", "config": rate_limit_config}

@subapp.get("/admin/rate-limit")
def get_rate_limit(
    user: Annotated[User, Depends(minimum_role(UserRole.ADMIN))]
):
    return rate_limit_config

@subapp.post("/upload/test")
async def test_upload(
    archive:          UploadFile,
    hash:             str,
    user: Annotated[User, Depends(require_login)],
):
    await test_upload_archive(archive,hash,user)
