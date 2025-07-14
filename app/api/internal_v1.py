
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import UUID4
from sqlmodel import Session

from app.core.dependencies import RateLimiter, oauth2_scheme
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

@subapp.get("/review-image", dependencies=[Depends(RateLimiter(requests_limit=5, time_window=5))])
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

@subapp.put("/review-image", dependencies=[Depends(RateLimiter(requests_limit=5, time_window=5))])
def update_image_review_status(token: Annotated[str, Depends(oauth2_scheme)]):
    pass

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
