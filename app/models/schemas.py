from datetime import datetime, timezone
from typing import Any, Dict
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlmodel import JSON, Field, SQLModel

from app.core import config
from app.models.models import UploadStatus, UserRole


class User(SQLModel, table=True):
    __tablename__ = "users" # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, max_length=config.MAX_USERNAME_LEN)
    email: EmailStr | None = Field(default=None, unique=True, nullable=True)
    password: str | None = Field(default=None, max_length=config.MAX_PASSWORD_LENGTH)
    disabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    team: int | None = Field(default=None, foreign_key="teams.id", index=True)
    role: UserRole = Field(default=UserRole.DEFAULT)
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
    status: UploadStatus = Field()
    file_size: int | None = Field(default=None, ge=0, le=config.MAX_FILE_SIZE)
    images_valid: int = Field(default=0, ge=0)
    images_rejected: int = Field(default=0, ge=0)
    images_total: int = Field(default=0, ge=0)
    capture_time: datetime = Field()
    start_time: datetime | None = Field(default=None)
    estimated_processing_time_left: int | None = Field(default=None, ge=0)
    error_message: str | None = Field(default=None, max_length=500)

class Image(SQLModel, table=True):
    __tablename__ = "images" # type: ignore

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(index=True)
    created_by: int = Field(foreign_key="teams.id", index=True)
    batch: UUID = Field(foreign_key="upload_batches.id")
    labels: Dict[str, Any] | None = Field(default=None, sa_type=JSON)

class PreImage(SQLModel, table=True):
    __tablename__ = "pre_images" # type: ignore

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(index=True)
    created_by: int = Field(foreign_key="teams.id", index=True)
    batch: UUID = Field(foreign_key="upload_batches.id")
    labels: Dict[str, Any] | None = Field(default=None, sa_type=JSON)
    reviewed: bool = Field(default=False)
