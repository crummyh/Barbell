from datetime import datetime
from uuid import uuid4

from pydantic.types import UUID4
from sqlmodel import JSON, Field, SQLModel

from app.models.models import UploadStatus


class Team(SQLModel, table=True):
    __tablename__ = 'teams' # type: ignore

    id: int | None = Field(default=None, index=True, primary_key=True)
    team_number: int
    team_name: str | None
    created_at: datetime | None

    # Security:
    api_key: str | None = Field(index=True) # sha256 Hash, not full key
    email: str | None = None
    disabled: bool | None = None

class UploadBatch(SQLModel, table=True):
    __tablename__ = 'upload_batches' # type: ignore

    id: UUID4 | None = Field(default_factory=uuid4, index=True, primary_key=True)
    team_id: int = Field(foreign_key="teams.id", index=True)
    status: UploadStatus
    file_size: int | None
    images_valid: int = 0
    images_rejected: int = 0
    images_total: int = 0
    capture_time: datetime
    start_time: datetime | None = None
    estimated_processing_time_left: int | None = Field(default=None)
    error_message: str | None = None

class Image(SQLModel, table=True):
    __tablename__ = 'images' # type: ignore

    id: UUID4 | None = Field(index=True, primary_key=True)
    created_at: datetime
    created_by: int = Field(foreign_key="teams.id", index=True)
    batch: UUID4 = Field(foreign_key="upload_batches.id")
    labels: JSON | None = None
    # TODO: Implement Labels

class PreImage(SQLModel, table=True):
    __tablename__ = 'pre_images' # type: ignore

    id: UUID4 | None = Field(default_factory=uuid4, index=True, primary_key=True)
    created_at: datetime
    created_by: int = Field(foreign_key="teams.id", index=True)
    batch: UUID4 = Field(foreign_key="upload_batches.id")
    labels: JSON | None = None
    reviewed: bool = False
