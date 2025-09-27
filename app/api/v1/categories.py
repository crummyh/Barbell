from typing import Annotated

from fastapi import (
    APIRouter,
    HTTPException,
    Security,
)
from sqlmodel import select
from starlette.status import (
    HTTP_400_BAD_REQUEST,
)

from app.core.dependencies import (
    SessionDep,
    get_current_user,
    minimum_role,
)
from app.crud import label_category
from app.models.label_category import (
    LabelCategoryCreate,
    LabelCategoryPublic,
    LabelCategoryUpdate,
    LabelSuperCategory,
    LabelSuperCategoryCreate,
    LabelSuperCategoryPublic,
    LabelSuperCategoryUpdate,
)
from app.models.user import User, UserRole

router = APIRouter()


@router.post("/categories/super/create")
def create_label_super_category(
    category: LabelSuperCategoryCreate,
    session: SessionDep,
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))],
) -> LabelSuperCategoryPublic:
    try:
        return label_category.create_super(session, category).get_public()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from None


@router.get("/categories/super")
def get_label_super_categories(
    session: SessionDep,
    current_user: Annotated[User, Security(get_current_user)],
) -> list[LabelSuperCategoryPublic]:
    return [i.get_public() for i in session.exec(select(LabelSuperCategory)).all()]


@router.put("/categories/super/update")
def modify_label_super_category(
    id: int,
    update: LabelSuperCategoryUpdate,
    session: SessionDep,
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))],
) -> LabelSuperCategoryPublic:
    try:
        public_label = label_category.update_super(session, id, update)
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e)) from None
    if public_label is None:
        raise HTTPException(status_code=404, detail="Super Category not found")
    return public_label.get_public()


@router.delete("/categories/super/remove")
def remove_label_super_category(
    id: int,
    session: SessionDep,
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))],
) -> dict[str, str]:
    try:
        if label_category.delete_super(session, id) is True:
            return {"detail": "Successfully deleted"}
        else:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="Catagory does not exist"
            )
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e)) from None


@router.post("/categories/create")
def create_label_category(
    category: LabelCategoryCreate,
    session: SessionDep,
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))],
) -> LabelCategoryPublic:
    try:
        new_cat = label_category.create(session, category).get_public()
        assert isinstance(new_cat, LabelCategoryPublic)
        return new_cat
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from None


@router.delete("/categories/remove")
def remove_label_category(
    id: int,
    session: SessionDep,
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))],
) -> dict[str, str]:
    try:
        if label_category.delete(session, id) is True:
            return {"detail": "Successfully deleted"}
        else:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="Catagory does not exist"
            )
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e)) from None


@router.put("/categories/update")
def modify_label_category(
    id: int,
    update: LabelCategoryUpdate,
    session: SessionDep,
    current_user: Annotated[User, Security(minimum_role(UserRole.MODERATOR))],
) -> LabelCategoryPublic:
    try:
        public_label = label_category.update(session, id, update)
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e)) from None
    if public_label is None:
        raise HTTPException(status_code=404, detail="Super Category not found")
    return public_label.get_public()
