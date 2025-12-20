from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlmodel import JSON, Column, Field, Relationship, SQLModel

from app.core import config
from app.core.helpers import validated

if TYPE_CHECKING:
    from app.models.user import User


class DownloadStatus(str, Enum):
    STARTING = "starting"
    ASSEMBLING_LABELS = "assembling_labels"
    ASSEMBLING_IMAGES = "assembling_images"
    ADDING_MANIFEST = "adding_manifest"
    READY = "ready"
    FAILED = "failed"


class AnnotationSelection(BaseModel):
    id: int
    super: bool


class BaseDownloadBatch(SQLModel):
    status: "DownloadStatus" = Field(default=DownloadStatus.STARTING)
    non_match_images: bool = Field(default=True)
    image_count: int = Field(ge=1, le=config.MAX_DOWNLOAD_COUNT)
    annotations: list["AnnotationSelection"] = Field(sa_column=Column(JSON))
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    hash: str | None = Field(default=None)
    error_message: str | None = Field(default=None, max_length=500)


class DownloadBatch(BaseDownloadBatch, table=True):
    __tablename__ = "download_batches"  # type: ignore

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)

    user: "User" = Relationship(back_populates="download_batches")

    def get_public(self) -> "DownloadBatchPublic":
        public = validated(DownloadBatchPublic, self)
        public.username = self.user.username
        return public


class DownloadBatchCreate(SQLModel):
    annotations: list["AnnotationSelection"]
    count: int
    non_match_images: bool = True


class DownloadBatchUpdate(SQLModel):
    status: "DownloadStatus | None" = None
    non_match_images: bool | None = None
    image_count: int | None = None
    annotations: list["AnnotationSelection"] | None = None
    start_time: datetime | None = None
    hash: str | None = None
    error_message: str | None = None
    user: "User | None" = None


class DownloadBatchPublic(BaseDownloadBatch):
    id: UUID
    estimated_time_left: float
