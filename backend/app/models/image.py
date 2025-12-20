from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from app.core.helpers import validated

if TYPE_CHECKING:
    from app.models.annotation import Annotation, AnnotationPublic


class ImageReviewStatus(str, Enum):
    APPROVED = "approved"
    AWAITING_LABELS = "awaiting_labels"
    NOT_REVIEWED = "not_reviewed"


class ImageBase(SQLModel):
    created_by: int = Field(foreign_key="users.id", index=True)
    batch: UUID = Field(foreign_key="upload_batches.id")
    review_status: ImageReviewStatus = Field(
        default=ImageReviewStatus.NOT_REVIEWED, index=True
    )


class Image(ImageBase, table=True):
    __tablename__ = "images"  # type: ignore

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime | None = Field(
        index=True, default_factory=lambda: datetime.now(timezone.utc)
    )

    annotations: list["Annotation"] = Relationship(
        back_populates="image", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    def get_public(self) -> "ImagePublic":
        public = validated(ImagePublic, self)
        public.annotations = [i.get_public() for i in self.annotations]
        return public


class ImageCreate(SQLModel):
    batch: UUID


class ImageUpdate(SQLModel):
    created_at: datetime | None = None
    created_by: int | None = None
    batch: UUID | None = None
    review_status: ImageReviewStatus | None = None

    annotations: list["Annotation"] | None = None


class ImagePublic(ImageBase):
    id: UUID
    created_at: datetime
    annotations: list["AnnotationPublic"]
