from sqlmodel import Session

from app.models.models import (
    LabelCategory,
    LabelCategoryCreate,
    LabelCategoryUpdate,
    LabelSuperCategory,
    LabelSuperCategoryUpdate,
)


def create(
    session: Session,
    label_category_create: LabelCategoryCreate
) -> LabelCategory | LabelSuperCategory:
    if label_category_create.super_category_id:
        label_category = LabelCategory.model_validate(label_category_create)
    else:
        label_category = LabelSuperCategory.model_validate(label_category_create)
    session.add(label_category)
    session.commit()
    session.refresh(label_category)
    return label_category

def get(
    session: Session,
    id: int,
    super: bool = False
) -> LabelCategory | LabelSuperCategory | None:
    if super:
        label_category = session.get(LabelCategory, id)
    else:
        label_category = session.get(LabelSuperCategory, id)
    return label_category

def get_super(
    session: Session,
    id: int
) -> LabelSuperCategory | None:
    label_super_category = session.get(LabelSuperCategory, id)
    return label_super_category

def update(
    session: Session,
    id: int,
    label_category_update: LabelCategoryUpdate | dict
) -> LabelCategory | None:
    label_category = session.get(LabelCategory, id)
    if label_category is None:
        return None

    if isinstance(label_category_update, dict):
        label_category_update = AnnotationCreate(**label_category_update)

    new_label_category_data = label_category_update.model_dump(exclude_unset=True)
    label_category.sqlmodel_update(new_label_category_data)
    session.add(label_category)
    session.commit()
    session.refresh(label_category)
    return label_category

def update_super(
    session: Session,
    id: int,
    label_category_update: LabelSuperCategoryUpdate | dict
) -> LabelSuperCategory | None:
    label_category = session.get(LabelSuperCategory, id)
    if label_category is None:
        return None

    if isinstance(label_category_update, dict):
        label_category_update = AnnotationCreate(**label_category_update)

    new_label_category_data = label_category_update.model_dump(exclude_unset=True)
    label_category.sqlmodel_update(new_label_category_data)
    session.add(label_category)
    session.commit()
    session.refresh(label_category)
    return label_category

def delete(session: Session, id: int, super: bool = False) -> bool:
    if super:
        label_category = session.get(LabelSuperCategory, id)
    else:
        label_category = session.get(LabelCategory, id)

    if label_category is None:
        return False

    session.delete(label_category)
    session.commit()
    return True

def delete_super(session: Session, id: int) -> bool:
    label_category = session.get(LabelSuperCategory, id)
    if label_category is None:
        return False

    session.delete(label_category)
    session.commit()
    return True
