from __future__ import annotations

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import BinaryIO, List, Optional
from uuid import UUID, uuid4

from fastapi import Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr
from sqlmodel import Column, Field, ForeignKey, Integer, Relationship, SQLModel

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

class UserCreate(UserBase):
    password: str = Field(max_length=config.MAX_PASSWORD_LENGTH, min_length=config.MIN_PASSWORD_LENGTH)

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

class Team(TeamBase, table=True):
    __tablename__ = "teams" # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    disabled: bool = Field(default=False)

class TeamCreate(SQLModel):
    team_number: int
    team_name: str

class TeamUpdate(SQLModel):
    team_number: int | None = None
    team_name: str | None = None
    leader_user: int | None = None

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

# ==========={ DownloadBatch }=========== #



# ==========={ Image }=========== #



# ==========={ Annotation }=========== #



# ==========={ LabelCategory }=========== #


# ==========={ Random }=========== #

class AnnotationSelection(BaseModel):
    id: int
    super: bool

# ==========={ Responses }=========== #

class StatsOut(BaseModel):
    image_count: int
    un_reviewed_image_count: int
    team_count: int
    # years_available: list[int]
    # labels: dict[str, list[str]]
    uptime: timedelta

class TeamStatsOut(BaseModel):
    image_count: int
    un_reviewed_image_count: int
    years_available: set[int]
    upload_batches: int

class UploadStatusOut(BaseModel):
    batch_id: UUID
    user: str
    status: UploadStatus
    file_size: Optional[int]
    images_valid: Optional[int]
    images_rejected: Optional[int]
    images_total: Optional[int]
    estimated_time_left: Optional[float]
    error_msg: Optional[str]

class DownloadStatusOut(BaseModel):
    id: UUID | None
    user: str
    status: DownloadStatus
    non_match_images: bool
    image_count: int | None
    annotations: List[AnnotationSelection]
    start_time: datetime
    hash: str | None
    error_message: str | None

class UserOut(BaseModel):
    username: str
    email: EmailStr | None
    disabled: bool
    created_at: datetime
    team_number: int
    role: UserRole

# ==========={ Requests }=========== #

class DownloadRequest(BaseModel):
    annotations: List[AnnotationSelection]
    count: int
    non_match_images: bool = True

class NewUserData(BaseModel):
    username: str
    email: EmailStr
    password: str
    team: Optional[int] = None

class NewTeamData(BaseModel):
    team_number: int
    team_name: str
    leader_username: str

def image_response(file: BinaryIO) -> Response:
    file.seek(0)
    return StreamingResponse(
        file,
        media_type="image",
        headers={
            "Content-Disposition": "attachment"
        }
    )

class RateLimitUpdate(BaseModel):
    route: str
    requests_limit: int
    time_window: int

# ==========={ Responses and Requests }=========== #

class ReviewMetadata(BaseModel):
    id: UUID
    annotations: List["Annotation"] # Use [] for None
    created_at: datetime
    created_by: int
    batch: UUID
    review_status: ImageReviewStatus

# ==========={ Security }=========== #

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None

# I'm sorry
from app.models.schemas import Annotation  # noqa: E402

ReviewMetadata.model_rebuild()
