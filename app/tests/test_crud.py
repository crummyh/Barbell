from datetime import datetime

import pytest
from sqlmodel import Session

from app.crud import download_batch as download_batch_crud
from app.crud import image as image_crud
from app.crud import team as team_crud
from app.crud import upload_batch as upload_batch_crud
from app.crud import user as user_crud
from app.models.models import (
    DownloadBatch,
    DownloadBatchCreate,
    Image,
    ImageCreate,
    Team,
    TeamCreate,
    UploadBatch,
    UploadBatchCreate,
    User,
    UserCreate,
)


@pytest.fixture
def test_user(session):
    return user_crud.create(session, UserCreate(username="fixture", email="fixture@test.com", password="pw"))


@pytest.fixture
def test_batch(session, test_user):
    return upload_batch_crud.create(
        session,
        UploadBatchCreate(capture_time=datetime.now(), file_size=1111, user_id=test_user.id),
    )

@pytest.mark.parametrize(
    "model, create_schema, crud_module, delete, kwargs",
    [
        (User, UserCreate, user_crud, True, {"username": "test", "email": "test@example.com", "password": "testPassword"}),
        (User, UserCreate, user_crud, False, {"username": "test", "email": "test@example.com", "password": "testPassword"}),
        (Team, TeamCreate, team_crud, True, {"team_number": 4786, "team_name": "Nicolet FEAR", "leader_username": "test"}),
        (UploadBatch, UploadBatchCreate, upload_batch_crud, False, {"capture_time": datetime.now(), "file_size": 2 * 1024 * 1024, "user_id": 2}),
        (DownloadBatch, DownloadBatchCreate, download_batch_crud, True, {"annotations": {}, "count": 100, "non_match_images": False}),
        (Image, ImageCreate, image_crud, True, {}),
    ],
)
def test_crud_cycle(session: Session, model, create_schema, crud_module, delete, kwargs, test_batch):
    if model is Image:
        kwargs["batch"] = test_batch.id
    
    # Create
    obj_in = create_schema(**kwargs)
    obj = crud_module.create(session, obj_in)
    assert obj.id is not None

    # Get
    got = crud_module.get(session, obj.id)
    assert got is not None
    assert got.id == obj.id

    # Update
    if model is User:
        updated = crud_module.update(session, obj.id, )
        
    if hasattr(model, "review_status"):
        updated = crud_module.update(session, obj.id, {"review_status": "APPROVED"})
        assert updated.review_status == "APPROVED"

    # Delete
    if delete:
        deleted = crud_module.delete(session, obj.id)
        assert deleted is True
        assert crud_module.get(session, obj.id) is None
