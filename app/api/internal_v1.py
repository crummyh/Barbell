
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import UUID4
from sqlmodel import Session
from starlette.status import HTTP_404_NOT_FOUND

from app.core.dependencies import RateLimiter, oauth2_scheme, require_role
from app.core.helpers import (
    get_id_from_team_number,
    get_pre_image_all,
    get_pre_image_labeled,
    get_team_number_from_id,
    get_user_from_username,
)
from app.db.database import get_session
from app.models.models import ReviewMetadata, UserRole, image_response
from app.models.schemas import Image, PreImage, User
from app.services import buckets

subapp = FastAPI()
origins = [ # TODO: UPDATE WITH ACTUAL URL
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
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_session)],
    only_labeled: bool = True
) -> ReviewMetadata:
    if only_labeled:
        image = get_pre_image_labeled(session)
    else:
        image = get_pre_image_all(session)

    assert image.id
    return ReviewMetadata(
        id=image.id,
        annotations=image.annotations,
        created_at=image.created_at,
        created_by=get_team_number_from_id(image.created_by, session),
        batch=image.batch,
        reviewed=image.reviewed
    )

@subapp.put("/review-image", dependencies=[Depends(RateLimiter(requests_limit=5, time_window=5))])
def update_image_review_status(
    new_data: ReviewMetadata,
    session: Annotated[Session, Depends(get_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
    approve: bool = True
):
    pre_image = session.get(PreImage, new_data.id)
    if not pre_image:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    if not approve:
        pre_image.batch = new_data.batch
        pre_image.created_at = new_data.created_at
        pre_image.created_by = get_id_from_team_number(new_data.created_by, session)
        pre_image.id = new_data.id
        pre_image.annotations = new_data.annotations
        pre_image.reviewed = new_data.reviewed
        session.add(pre_image)

    else:
        image = Image(
            id=new_data.id,
            created_at=new_data.created_at,
            created_by=get_id_from_team_number(new_data.created_by, session),
            batch=new_data.batch,
            annotations=new_data.annotations
        )
        session.add(image)
        session.delete(pre_image)

    session.commit()

@subapp.get("/image/{image_id}", dependencies=[Depends(RateLimiter(requests_limit=5, time_window=5))])
def get_image(
    image_id: UUID4,
    token: Annotated[str, Depends(oauth2_scheme)],
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
    user = get_user_from_username(username, session)
    user.role = new_role
    session.add(user)
    session.commit()
