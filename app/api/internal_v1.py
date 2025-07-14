
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import UUID4
from sqlmodel import Session

from app.core.dependencies import oauth2_scheme
from app.core.helpers import get_most_recent_pre_image
from app.db.database import get_session
from app.models.models import ReviewMetadata, image_response
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

@subapp.get("/review-image")
def get_image_for_review(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session)
) -> ReviewMetadata:
    # Security goes here
    image = get_most_recent_pre_image(session)
    assert image.labels
    assert image.id
    return ReviewMetadata(
        id = image.id.hex,
        labels = image.labels
    )

@subapp.get("/image/{image_id}")
def get_image(
    image_id: UUID4,
    token: Annotated[str, Depends(oauth2_scheme)],
):
    return image_response(buckets.get_image(image_id))

@subapp.put("/review-image")
def update_image_review_status(token: Annotated[str, Depends(oauth2_scheme)]):
    # Security goes here
    pass
@subapp.post("/token")
def redirect_token():
    """
    Redirects requests from here to the main auth router
    """
    return RedirectResponse(url="/token", status_code=307)


# @subapp.get("/test")
# def read_users_me(
#     current_user: Annotated[User, Depends(minimum_role(UserRole.MODERATOR))],
# ):
#     return current_user

@subapp.put("/rollback-db")
def rollback_database(
    session: Annotated[Session, Depends(get_session)]
):
    session.rollback()
