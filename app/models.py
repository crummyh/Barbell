from datetime import datetime

from sqlmodel import Field, SQLModel

# ==========={ Tables }=========== #

class Team(SQLModel, table=True):
    id: int = Field(index=True, primary_key=True)
    team_number: int
    team_name: str | None
    api_key: str | None # Hash, not full key
    created_at: datetime | None

class UploadBatch(SQLModel, table=True):
    id: int = Field(index=True, primary_key=True)
    team_id: int = Field(foreign_key=Team.id)
    file_size: int | None
    images_valid: int = 0
    images_rejected: int = 0
    image_total: int | None
    processing_time: int | None

class Image(SQLModel, table=True):
    id: int = Field(index=True, primary_key=True)
    hash: str | None
    created_at: datetime
    created_by: int = Field(foreign_key=Team.id)
    batch: int = Field(foreign_key=UploadBatch.id)

# ==========={ Other }=========== #
