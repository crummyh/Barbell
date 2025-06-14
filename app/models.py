from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from sqlmodel import Field, SQLModel

# ==========={ Enums & States }=========== #

class UploadStatus(Enum):
    UPLOADING  = "uploading"
    PROCESSING = "processing"
    COMPLETED  = "completed"
    FAILED     = "failed"

# ==========={ Tables }=========== #

class Team(SQLModel, table=True):
    __tablename__ = 'teams' # type: ignore

    id: int | None = Field(default=None, index=True, primary_key=True)
    team_number: int
    team_name: str | None
    api_key: str | None = Field(index=True) # Hash, not full key
    created_at: datetime | None

class UploadBatch(SQLModel, table=True):
    __tablename__ = 'upload_batches' # type: ignore

    id: int | None = Field(default=None, index=True, primary_key=True)
    team_id: int = Field(foreign_key="teams.id")
    status: UploadStatus
    file_size: int | None
    images_valid: int = 0
    images_rejected: int = 0
    images_total: int | None = Field(default=None)
    processing_time: int | None = Field(default=None)

class Image(SQLModel, table=True):
    __tablename__ = 'images' # type: ignore

    id: int | None = Field(default=None, index=True, primary_key=True)
    hash: str | None
    created_at: datetime
    created_by: int = Field(foreign_key="teams.id")
    batch: int = Field(foreign_key="upload_batches.id")

# ==========={ Other }=========== #

class StatsOut(BaseModel):
    image_count: int
    team_count: int
    # years_available: list[int]
    # labels: dict[str, list[str]]
    # uptime: str

class TeamStatsOut(BaseModel):
    image_count: int
    years_available: list[int]
    upload_batches: int

class StatusOut(BaseModel):
    batch_id: int
    team: int
    status: UploadStatus
    file_size: int
    images_valid: int
    images_rejected: int
    images_total: int
    file_path: str | None
    error_msg: str | None
