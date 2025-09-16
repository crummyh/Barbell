from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.image import Image

class AnnotationSelection(BaseModel):
    id: int
    super: bool

class AnnotationBase(SQLModel):
    category_id: int = Field(foreign_key="label_categories.id", index=True)
    iscrowd: bool = Field(default=False)
    area: float | None = Field(default=None)
    bbox_x: int | None = Field(default=None)
    bbox_y: int | None = Field(default=None)
    bbox_w: int | None = Field(default=None)
    bbox_h: int | None = Field(default=None)

    def set_bbox(self, bbox: tuple[int,int,int,int]):
        self.bbox_x = bbox[0]
        self.bbox_y = bbox[1]
        self.bbox_w = bbox[2]
        self.bbox_h = bbox[3]

class Annotation(AnnotationBase, table=True):
    __tablename__ = "annotations" # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    image_id: UUID = Field(foreign_key="images.id", index=True)

    image: "Image" = Relationship(back_populates="annotations")

    def get_public(self) -> "AnnotationPublic":
        return AnnotationPublic.model_validate(self)

class AnnotationCreate(AnnotationBase):
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
