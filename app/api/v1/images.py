from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Security,
)
from fastapi.responses import StreamingResponse
from sqlmodel import asc, select
from starlette.status import (
    HTTP_404_NOT_FOUND,
)

from app.core.dependencies import (
    RateLimiter,
    SessionDep,
    minimum_role,
    require_role,
)
from app.crud import image, user
from app.models.image import Image, ImagePublic, ImageReviewStatus, ImageUpdate
from app.models.models import (
    image_response,
)
from app.models.user import User, UserPublic, UserRole, UserUpdate
from app.services import buckets

router = APIRouter()


@router.get(
    "", dependencies=[Depends(RateLimiter(requests_limit=5, time_window=5))]
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
    "",
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
    "/{image_id}",
    dependencies=[Depends(RateLimiter(requests_limit=5, time_window=5))],
)
def get_image_by_id(
    image_id: UUID,
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))],
) -> StreamingResponse:
    return image_response(buckets.get_image(image_id))
