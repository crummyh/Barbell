from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlalchemy import Column, String
from sqlmodel import Field, Relationship, Session, SQLModel

import app.models.models as models
from app.core import config


class User(SQLModel, table=True):
    __tablename__ = "users" # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, max_length=config.MAX_USERNAME_LEN)
    email: EmailStr | None = Field(default=None, unique=True, nullable=True)
    password: str | None = Field(default=None, max_length=config.MAX_PASSWORD_LENGTH)
    disabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    team: int | None = Field(default=None, foreign_key="teams.id", index=True)
    role: models.UserRole = Field(default=models.UserRole.DEFAULT)
    code: str | None = Field(max_length=config.VERIFICATION_CODE_STR_LEN)

class Team(SQLModel, table=True):
    __tablename__ = "teams" # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    team_number: int = Field(index=True, unique=True, ge=0, le=config.MAX_TEAM_NUMB)
    team_name: str | None = Field(default=None, max_length=config.MAX_TEAM_NAME_LEN)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    api_key: str | None = Field(default=None, index=True, unique=True)
    disabled: bool = Field(default=False)
    leader_user: int | None = Field(default=None, foreign_key="users.id", index=True)

class UploadBatch(SQLModel, table=True):
    __tablename__ = "upload_batches" # type: ignore

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    team: int = Field(foreign_key="teams.id", index=True)
    status: models.UploadStatus = Field()
    file_size: int | None = Field(default=None, ge=0, le=config.MAX_FILE_SIZE)
    images_valid: int = Field(default=0, ge=0)
    images_rejected: int = Field(default=0, ge=0)
    images_total: int = Field(default=0, ge=0)
    capture_time: datetime = Field()
    start_time: datetime | None = Field(default=None)
    estimated_processing_time_left: int | None = Field(default=None, ge=0)
    error_message: str | None = Field(default=None, max_length=500)

class AnnotatableType(str, Enum):
    image = "image"
    preimage = "preimage"

class Annotation(SQLModel, table=True):
    __tablename__ = "annotations" # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    image_type: AnnotatableType = Field(sa_column=Column(String, nullable=False))
    image_id: int # ID of an Image or PreImage
    catagory_id: int = Field(foreign_key="label_categories.id", index=True)
    iscrowd: bool = Field(default=False)
    area: float | None = Field(default=None)
    bbox_x: int | None = Field(default=None)
    bbox_y: int | None = Field(default=None)
    bbox_w: int | None = Field(default=None)
    bbox_h: int | None = Field(default=None)

def get_annotation_target(session: Session, annotation: Annotation) -> Image | PreImage | None:
    if annotation.image_type == AnnotatableType.image:
        return session.get(Image, annotation.image_id)
    elif annotation.image_type == AnnotatableType.preimage:
        return session.get(PreImage, annotation.image_id)

def set_bbox(annotation: Annotation, bbox: tuple[int,int,int,int]):
    annotation.bbox_x = bbox[0]
    annotation.bbox_y = bbox[1]
    annotation.bbox_w = bbox[2]
    annotation.bbox_h = bbox[3]

class LabelSuperCatagory(SQLModel, table=True):
    __tablename__ = "label_super_categories" # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    name: str | None = Field()

class LabelCatagory(SQLModel, table=True):
    __tablename__ = "label_categories" # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field()
    super_category: int | None = Field(foreign_key="label_super_categories.id")

class Image(SQLModel, table=True):
    __tablename__ = "images" # type: ignore

    id: UUID = Field(primary_key=True)
    created_at: datetime = Field(index=True)
    created_by: int = Field(foreign_key="teams.id", index=True)
    batch: UUID = Field(foreign_key="upload_batches.id")

    annotations: Optional[List[Annotation]] = Relationship(back_populates="image")

class PreImage(SQLModel, table=True):
    __tablename__ = "pre_images" # type: ignore

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(index=True)
    created_by: int = Field(foreign_key="teams.id", index=True)
    batch: UUID = Field(foreign_key="upload_batches.id")
    reviewed: bool = Field(default=False)

    annotations: Optional[List[Annotation]] = Relationship(back_populates="image")
