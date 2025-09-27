from typing import Annotated

from fastapi import (
    APIRouter,
    HTTPException,
    Security,
)

from app.core.dependencies import (
    SessionDep,
    generate_api_key,
    get_current_user,
)
from app.models.user import User

router = APIRouter()


@router.put("/api-key")
def create_or_rotate_api_key(
    session: SessionDep,
    current_user: Annotated[User, Security(get_current_user)],
) -> str:
    try:
        current_user.api_key = generate_api_key()
        return current_user.api_key
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to change API key"
        ) from None
