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

@router.put(
    "/user/update", dependencies=[Depends(RateLimiter(requests_limit=5, time_window=5))]
)
def update_user(
    username: str,
    user_update: UserUpdate,
    session: SessionDep,
    current_user: Annotated[User, Security(require_role(UserRole.ADMIN))],
) -> UserPublic:
    db_user = user.get_user_from_username(session, username)
    if db_user is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")

    try:
        assert db_user.id
        user.update(session, db_user.id, user_update)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from None
    else:
        return db_user.get_public()