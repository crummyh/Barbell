from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4

from sqlmodel import JSON, Column, Field, Relationship, SQLModel

import app.models.models as models
from app.core import config

# class User(SQLModel, table=True):
#     __tablename__ = "users" # type: ignore

#     id: int | None = Field(default=None, primary_key=True)
#     username: str = Field(index=True, max_length=config.MAX_USERNAME_LEN, min_length=config.MIN_USERNAME_LEN)
#     email: EmailStr | None = Field(default=None, unique=True, nullable=True)
#     password: str | None = Field(default=None, max_length=config.MAX_PASSWORD_LENGTH, min_length=config.MIN_PASSWORD_LENGTH)
#     api_key: str | None = Field(default=None, index=True, unique=True)
#     disabled: bool = Field(default=True)
#     created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
#     team: int | None = Field(default=None, foreign_key="teams.id", index=True)
#     role: models.UserRole = Field(default=models.UserRole.DEFAULT)
#     code: str | None = Field(max_length=config.VERIFICATION_CODE_STR_LEN)

# class Team(SQLModel, table=True):
#     __tablename__ = "teams" # type: ignore

#     id: int | None = Field(default=None, primary_key=True)
#     team_number: int = Field(index=True, unique=True, ge=0, le=config.MAX_TEAM_NUMB)
#     team_name: str | None = Field(default=None, max_length=config.MAX_TEAM_NAME_LEN)
#     created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
#     disabled: bool = Field(default=False)
#     leader_user: int | None = Field(
#         default=None,
#         sa_column=Column(
#             Integer,
#             ForeignKey("users.id", use_alter=True, name="fk_team_leader_user")
#         ),
#     )

# class UploadBatch(SQLModel, table=True):
#     __tablename__ = "upload_batches" # type: ignore

#     id: UUID | None = Field(default_factory=uuid4, primary_key=True)
#     user: int = Field(foreign_key="users.id", index=True)
#     status: models.UploadStatus = Field()
#     file_size: int | None = Field(default=None, ge=0, le=config.MAX_FILE_SIZE)
#     images_valid: int = Field(default=0, ge=0)
#     images_rejected: int = Field(default=0, ge=0)
#     images_total: int = Field(default=0, ge=0)
#     capture_time: datetime = Field()
#     start_time: datetime | None = Field(default=None)
#     error_message: str | None = Field(default=None, max_length=500)

class DownloadBatch(SQLModel, table=True):
    __tablename__ = "download_batches" # type: ignore

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    user: int = Field(foreign_key="users.id")
    status: models.DownloadStatus = Field()
    non_match_images: bool = Field(default=True)
    image_count: int = Field(ge=1, le=config.MAX_DOWNLOAD_COUNT)
    annotations: List[models.AnnotationSelection] = Field(sa_column=Column(JSON))
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    hash: str | None = Field(default=None)
    error_message: str | None = Field(default=None, max_length=500)

class Image(SQLModel, table=True):
    __tablename__ = "images" # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(index=True)
    created_by: int = Field(foreign_key="users.id", index=True)
    batch: UUID = Field(foreign_key="upload_batches.id")
    review_status: models.ImageReviewStatus = Field(default=models.ImageReviewStatus.NOT_REVIEWED, index=True)

    annotations: List["Annotation"] = Relationship(back_populates="image", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

class Annotation(SQLModel, table=True):
    __tablename__ = "annotations" # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    image_id: UUID = Field(foreign_key="images.id")
    category_id: int = Field(foreign_key="label_categories.id", index=True)
    iscrowd: bool = Field(default=False)
    area: float | None = Field(default=None)
    bbox_x: int | None = Field(default=None)
    bbox_y: int | None = Field(default=None)
    bbox_w: int | None = Field(default=None)
    bbox_h: int | None = Field(default=None)

    image: Image = Relationship(back_populates="annotations")

def set_bbox(annotation: Annotation, bbox: tuple[int,int,int,int]):
    annotation.bbox_x = bbox[0]
    annotation.bbox_y = bbox[1]
    annotation.bbox_w = bbox[2]
    annotation.bbox_h = bbox[3]

class LabelSuperCategory(SQLModel, table=True):
    __tablename__ = "label_super_categories" # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    name: str | None = Field()

    sub_categories: List["LabelCategory"] = Relationship(back_populates="super_category")

class LabelCategory(SQLModel, table=True):
    __tablename__ = "label_categories" # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field()
    super_category_id: int | None = Field(foreign_key="label_super_categories.id")

    super_category: Optional[LabelSuperCategory] = Relationship(back_populates="sub_categories")
