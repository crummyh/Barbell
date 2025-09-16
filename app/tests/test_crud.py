from datetime import datetime

import pytest
from sqlmodel import Session

from app.crud import annotation as annotation_crud
from app.crud import download_batch as download_batch_crud
from app.crud import image as image_crud
from app.crud import team as team_crud
from app.crud import label_category as label_category_crud
from app.crud import upload_batch as upload_batch_crud
from app.crud import user as user_crud
from app.crud.base import CRUDModuleProtocol
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

def test_crud_layers_protocol()):
    protocols = [
        annotation,
        download_batch_crud,
        image_crud,
        team_crud,
        label_category_crud,
        upload_batch_crud,
        user_crud
    ]
    for proto in protocols:
        assert isinstance(proto, CRUDModuleProtocol)

def generic_test_crud(
    crud_module: CRUDModuleProtocol[ModelType, CreateSchemaType, UpdateSchemaType],
    session: Session,
    create_data: CreateSchemaType,
    update_data: UpdateSchemaType
) -> None:
    """Generic test that works with any CRUD module."""
    
    # Test create
    created = crud_module.create(session, create_data)
    assert created is not None
    
    # Test get
    retrieved = crud_module.get(session, created.id)  # type: ignore
    assert retrieved is not None
    
    # Test update
    updated = crud_module.update(session, created.id, update_data)  # type: ignore
    assert updated is not None
    
    # Test delete
    deleted = crud_module.delete(session, created.id)  # type: ignore
    assert deleted is True

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