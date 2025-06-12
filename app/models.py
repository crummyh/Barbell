from datetime import datetime

from pydantic import BaseModel
from sqlmodel import Field, SQLModel

# ==========={ Tables }=========== #

class Team(SQLModel, table=True):
    __tablename__ = 'teams' # type: ignore

    id: int = Field(index=True, primary_key=True)
    team_number: int
    team_name: str | None
    api_key: str | None # Hash, not full key
    created_at: datetime | None

class UploadBatch(SQLModel, table=True):
    __tablename__ = 'upload_batches' # type: ignore

    id: int = Field(index=True, primary_key=True)
    team_id: int = Field(foreign_key="teams.id")
    file_size: int | None
    images_valid: int = 0
    images_rejected: int = 0
    image_total: int | None
    processing_time: int | None

class Image(SQLModel, table=True):
    __tablename__ = 'images' # type: ignore

    id: int = Field(index=True, primary_key=True)
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
    pass

class StatusOut(BaseModel):
    pass
