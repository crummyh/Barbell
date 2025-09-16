from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from app.core import config

if TYPE_CHECKING:
    from app.models.user import User

class UploadStatus(str, Enum):
    UPLOADING  = "uploading"
    PROCESSING = "processing"
    COMPLETED  = "completed"
    FAILED     = "failed"

class BaseUploadBatch(SQLModel):
    status: UploadStatus = Field(default=UploadStatus.UPLOADING)
    file_size: int | None = Field(default=None, ge=0, le=config.MAX_FILE_SIZE)
    images_valid: int = Field(default=0, ge=0)
    images_rejected: int = Field(default=0, ge=0)
    images_total: int = Field(default=0, ge=0)
    capture_time: datetime = Field()
    start_time: datetime | None = Field(default=None)
    error_message: str | None = Field(default=None, max_length=500)

class UploadBatch(BaseUploadBatch, table=True):
    __tablename__ = "upload_batches" # type: ignore

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)

    user: "User" = Relationship(back_populates="upload_batches")

    def get_public(self) -> "UploadBatchPublic":
        public = UploadBatchPublic.model_validate(self)
        public.username = self.user.username
        return public

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
    username: str
    estimated_time_left: float
