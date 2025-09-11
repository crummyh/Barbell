from __future__ import annotations

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import BinaryIO, List, Optional
from uuid import UUID, uuid4

from fastapi import Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr
from sqlmodel import JSON, Column, Field, ForeignKey, Integer, Relationship, SQLModel

from app.core import config

# ==========={ Enums & States }=========== #

class UploadStatus(Enum):
    UPLOADING  = "uploading"
    PROCESSING = "processing"
    COMPLETED  = "completed"
    FAILED     = "failed"

class DownloadStatus(Enum):
    STARTING = "starting"
    ASSEMBLING_LABELS = "assembling_labels"
    ASSEMBLING_IMAGES = "assembling_images"
    ADDING_MANIFEST = "adding_manifest"
    READY = "ready"
    FAILED = "failed"

class UserRole(Enum):
    DEFAULT     = 0
    TEAM_LEADER = 1
    MODERATOR   = 2
    ADMIN       = 3

class ImageReviewStatus(Enum):
    APPROVED = "approved"
    AWAITING_LABELS = "awaiting_labels"
    NOT_REVIEWED = "not_reviewed"

# ==========={ Guild }=========== #
"""
A guild for separating schemas:
`___Base`: Common fields
`___`: db/internal only fields
`___Create`: Fields that are not controlled by the database and needed
`___Public`: Fields that need to be accessed, but need a different definition then in the db
"""

# ==========={ User }=========== #

class UserBase(SQLModel):
    username: str = Field(index=True, max_length=config.MAX_USERNAME_LEN, min_length=config.MIN_USERNAME_LEN)
    email: EmailStr = Field(unique=True)
    led_team: "Team" = Relationship(back_populates="leader")

class User(UserBase, table=True):
    __tablename__ = "users" # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    disabled: bool = Field(default=True)
    team: int | None = Field(default=None, foreign_key="teams.id", index=True)
    api_key: str | None = Field(default=None, index=True, unique=True)
    password: str = Field(max_length=config.MAX_PASSWORD_LENGTH, min_length=config.MIN_PASSWORD_LENGTH)
    role: UserRole = Field(default=UserRole.DEFAULT)
    code: str | None = Field(max_length=config.VERIFICATION_CODE_STR_LEN)

    def get_public(self) -> "UserPublic":
        return UserPublic.model_validate(self)

class UserCreate(UserBase):
    password: str

class UserUpdate(SQLModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = Field(
        default=None,
        max_length=config.MAX_PASSWORD_LENGTH,
        min_length=config.MIN_PASSWORD_LENGTH,
    )
    disabled: bool | None = None
    team: int | None = None
    role: UserRole | None = None
    code: str | None = None

class UserPublic(UserBase):
    id: int
    created_at: datetime
    disabled: bool
    role: UserRole
    team: int | None

# ==========={ Team }=========== #

class TeamBase(SQLModel):
    team_number: int = Field(index=True, unique=True, ge=0, le=config.MAX_TEAM_NUMB)
    team_name: str = Field(max_length=config.MAX_TEAM_NAME_LEN)
    leader_user: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("users.id", use_alter=True, name="fk_team_leader_user")
        ),
    )
    leader: "User" = Relationship(sa_relationship_kwargs={"foreign_keys": "Team.leader_user"})

    upload_batches: List["UploadBatch"] = Relationship(back_populates="user")
    download_batches: List["DownloadBatch"] = Relationship(back_populates="user")

class Team(TeamBase, table=True):
    __tablename__ = "teams" # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    disabled: bool = Field(default=False)

    def get_public(self) -> "TeamPublic":
        return TeamPublic.model_validate(self)

class TeamCreate(SQLModel):
    team_number: int
    team_name: str
    leader_username: str

class TeamUpdate(SQLModel):
    team_number: int | None = None
    team_name: str | None = None
    leader_username: str | None = None

class TeamPublic(TeamBase):
    id: int
    created_at: datetime
    disabled: bool

# ==========={ UploadBatch }=========== #

class BaseUploadBatch(SQLModel):

    status: UploadStatus = Field(default=UploadStatus.UPLOADING)
    file_size: int | None = Field(default=None, ge=0, le=config.MAX_FILE_SIZE)
    images_valid: int = Field(default=0, ge=0)
    images_rejected: int = Field(default=0, ge=0)
    images_total: int = Field(default=0, ge=0)
    capture_time: datetime = Field()
    start_time: datetime | None = Field(default=None)
    error_message: str | None = Field(default=None, max_length=500)

    user: User = Relationship(back_populates="upload_batches")

class UploadBatch(BaseUploadBatch, table=True):
    __tablename__ = "upload_batches" # type: ignore

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)

    def get_public(self) -> "UploadBatchPublic":
        return UploadBatchPublic.model_validate(self)

class UploadBatchCreate(SQLModel):
    capture_time: datetime
    file_size: int
    user_id: int

class UploadBatchUpdate(SQLModel):
   status: UploadStatus | None = None
   file_size: int | None = None
   images_valid: int | None = None
   images_rejected: int | None = None
   images_total: int | None = None
   capture_time: datetime | None = None
   start_time: datetime | None = None
   error_message: str | None = None
   user_id: int | None = None

class UploadBatchPublic(BaseUploadBatch):
    id: UUID
    estimated_time_left: float

# ==========={ DownloadBatch }=========== #

class BaseDownloadBatch(SQLModel):
    status: "DownloadStatus" = Field(default=DownloadStatus.STARTING)
    non_match_images: bool = Field(default=True)
    image_count: int = Field(ge=1, le=config.MAX_DOWNLOAD_COUNT)
    annotations: List["AnnotationSelection"] = Field(sa_column=Column(JSON))
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    hash: str | None = Field(default=None)
    error_message: str | None = Field(default=None, max_length=500)

    user: User = Relationship(back_populates="download_batches")

class DownloadBatch(BaseDownloadBatch, table=True):
    __tablename__ = "download_batches" # type: ignore

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    user_id: int = Field(foreign_key="users.id")

    def get_public(self) -> "DownloadBatchPublic":
        return DownloadBatchPublic.model_validate(self)

class DownloadBatchCreate(SQLModel):
    annotations: List["AnnotationSelection"]
    count: int
    non_match_images: bool = True

class DownloadBatchUpdate(SQLModel):
    status: "DownloadStatus | None" = None
    non_match_images: bool | None = None
    image_count: int | None = None
    annotations: List["AnnotationSelection"] | None = None
    start_time: datetime | None = None
    hash: str | None = None
    error_message: str | None = None
    user: User | None = None

class DownloadBatchPublic(BaseDownloadBatch):
    id: UUID
    estimated_time_left: float

# ==========={ Image }=========== #

class ImageBase(SQLModel):
    created_at: datetime = Field(index=True, default_factory=lambda: datetime.now(timezone.utc))
    created_by: int = Field(foreign_key="users.id", index=True)
    batch: UUID = Field(foreign_key="upload_batches.id")
    review_status: ImageReviewStatus = Field(default=ImageReviewStatus.NOT_REVIEWED, index=True)

    annotations: List["Annotation"] = Relationship(back_populates="image", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

class Image(ImageBase, table=True):
    __tablename__ = "images" # type: ignore

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)

    def get_public(self) -> "ImagePublic":
        return ImagePublic.model_validate(self)

class ImageCreate(SQLModel):
    batch: UUID

class ImageUpdate(SQLModel):
    created_at: datetime | None = None
    created_by: int | None = None
    batch: UUID | None = None
    review_status: ImageReviewStatus | None = None

    annotations: List["Annotation"] | None = None

class ImagePublic(ImageBase):
    id: UUID

# ==========={ Annotation }=========== #

class AnnotationBase(SQLModel, table=True):
    category_id: int = Field(foreign_key="label_categories.id", index=True)
    iscrowd: bool = Field(default=False)
    area: float | None = Field(default=None)
    bbox_x: int | None = Field(default=None)
    bbox_y: int | None = Field(default=None)
    bbox_w: int | None = Field(default=None)
    bbox_h: int | None = Field(default=None)

    image: Image = Relationship(back_populates="annotations")

    def set_bbox(self, bbox: tuple[int,int,int,int]):
        self.bbox_x = bbox[0]
        self.bbox_y = bbox[1]
        self.bbox_w = bbox[2]
        self.bbox_h = bbox[3]

class Annotation(AnnotationBase, table=True):
    __tablename__ = "annotations" # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    image_id: UUID = Field(foreign_key="images.id")

    def get_public(self) -> "AnnotationPublic":
        return AnnotationPublic.model_validate(self)

class AnnotationCreate(SQLModel):
    pass

class AnnotationUpdate(SQLModel):
    category_id: int | None = None
    iscrowd: bool | None = None
    area: float | None = None
    bbox_x: int | None = None
    bbox_y: int | None = None
    bbox_w: int | None = None
    bbox_h: int | None = None
    image_id: UUID | None = None

class AnnotationPublic(SQLModel):
    id: int
    image_id: UUID

# ==========={ LabelCategory }=========== #

class LabelCategoryBase(SQLModel):
    name: str = Field()

class LabelSuperCategory(LabelCategoryBase, table=True):
    __tablename__ = "label_super_categories" # type: ignore

    id: int | None = Field(default=None, primary_key=True)

    sub_categories: List["LabelCategory"] = Relationship(back_populates="super_category")

    def get_public(self) -> "LabelCategoryPublic":
        return LabelCategoryPublic.model_validate(self)

class LabelCategory(LabelCategoryBase, table=True):
    __tablename__ = "label_categories" # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    super_category_id: int | None = Field(foreign_key="label_super_categories.id")

    super_category: Optional[LabelSuperCategory] = Relationship(back_populates="sub_categories")

    def get_public(self) -> "LabelCategoryPublic":
        return LabelCategoryPublic.model_validate(self)

class LabelCategoryCreate(LabelCategoryBase):
    super_category_id: int | None = None

class LabelCategoryUpdate(SQLModel):
    name: str | None = None
    super_category_id: int | None = None

class LabelSuperCategoryUpdate(LabelCategoryUpdate):
    name: str | None = None

class LabelCategoryPublic(LabelCategoryBase):
    id: int
    super_category_id: int | None = None

# ==========={ Random }=========== #

class AnnotationSelection(BaseModel):
    id: int
    super: bool

# ==========={ Responses }=========== #

class StatsOut(BaseModel):
    image_count: int
    un_reviewed_image_count: int
    team_count: int
    uptime: timedelta

class TeamStatsOut(BaseModel):
    image_count: int
    un_reviewed_image_count: int
    years_available: set[int]
    upload_batches: int

def image_response(file: BinaryIO) -> Response:
    file.seek(0)
    return StreamingResponse(
        file,
        media_type="image",
        headers={
            "Content-Disposition": "attachment"
        }
    )

# ==========={ Requests }=========== #

class RateLimitUpdate(BaseModel):
    route: str
    requests_limit: int
    time_window: int

# ==========={ Security }=========== #

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None
