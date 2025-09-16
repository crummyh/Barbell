from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    pass

class LabelCategoryBase(SQLModel):
    name: str = Field()

class LabelSuperCategory(LabelCategoryBase, table=True):
    __tablename__ = "label_super_categories" # type: ignore

    id: int | None = Field(default=None, primary_key=True)

    sub_categories: List["LabelCategory"] = Relationship(back_populates="super_category")

    def get_public(self) -> "LabelSuperCategoryPublic":
        public = LabelSuperCategoryPublic.model_validate(self)
        public.sub_categories = [i.get_public() for i in self.sub_categories]
        return public

class LabelCategory(LabelCategoryBase, table=True):
    __tablename__ = "label_categories" # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    super_category_id: int | None = Field(foreign_key="label_super_categories.id")

    super_category: Optional[LabelSuperCategory] = Relationship(back_populates="sub_categories")

    def get_public(self) -> "LabelCategoryPublic":
        return LabelCategoryPublic.model_validate(self)

class LabelCategoryCreate(LabelCategoryBase):
    super_category_id: int | None

class LabelSuperCategoryCreate(LabelCategoryBase):
    pass

class LabelCategoryUpdate(SQLModel):
    name: str | None = None
    super_category_id: int | None = None

class LabelSuperCategoryUpdate(LabelCategoryUpdate):
    name: str | None = None

class LabelCategoryPublic(LabelCategoryBase):
    id: int
    super_category_id: int | None

class LabelSuperCategoryPublic(LabelCategoryBase):
    id: int
    sub_categories: List["LabelCategoryPublic"]
