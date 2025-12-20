from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from app.core import config
from app.core.dependencies import (
    RateLimiter,
    create_access_token,
    generate_api_key,
    generate_verification_code,
    get_current_user,
    get_password_hash,
    handle_raw_auth,
)
from app.crud import team, user
from app.database import get_session
from app.models.team import Team, TeamCreate
from app.models.user import User, UserCreate, UserPublic
from app.services.email.email import send_verification_email

router = APIRouter()


@router.post(
    "/token",
    tags=["Auth"],
    dependencies=[Depends(RateLimiter(requests_limit=10, time_window=5))],
)
def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)],
) -> JSONResponse:
    user = handle_raw_auth(
        session=session, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    assert user.role is not None
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.name},
        expires_delta=access_token_expires,
    )

    resp = JSONResponse(content={"message": "Login successful"})
    resp.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=config.IS_PRODUCTION,
        samesite="lax",
        max_age=60 * 60 * 24,
    )

    return resp


@router.get(
    "/users/me",
    tags=["Auth"],
    dependencies=[Depends(RateLimiter(requests_limit=10, time_window=5))],
)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserPublic:
    return current_user.get_public()


@router.post(
    "/register",
    tags=["Auth"],
    dependencies=[Depends(RateLimiter(requests_limit=1, time_window=10))],
)
def register_user(
    new_user: UserCreate,
    background_tasks: BackgroundTasks,
    session: Annotated[Session, Depends(get_session)],
) -> dict[str, str]:
    try:
        session.exec(select(User).where(User.email == new_user.email)).one()
    except Exception:
        pass
    else:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail="Email is taken"
        ) from None

    try:
        session.exec(select(User).where(User.username == new_user.username)).one()
    except Exception:
        pass
    else:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail="Username is taken"
        ) from None

    try:
        db_user = user.create(session, new_user)
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from None

    assert db_user.id
    user.update(session, db_user.id, {"code": generate_verification_code(session)})

    background_tasks.add_task(send_verification_email, db_user)
    return {"detail": "Successfully registered"}


@router.get(
    "/verify",
    tags=["Auth"],
    dependencies=[Depends(RateLimiter(requests_limit=2, time_window=10))],
)
def verify_email_code(
    code: str, session: Annotated[Session, Depends(get_session)]
) -> dict[str, str]:
    try:
        db_user = session.exec(select(User).where(User.code == code)).one()

    except Exception:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="Incorrect Verification Code"
        ) from None

    try:
        user.update(session, db_user.id, {"code": None, "disabled": False})

    except Exception:
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to modify user") from None
    else:
        return {"detail": "Successfully verified"}


@router.post(
    "/register/team",
    tags=["Auth"],
    dependencies=[Depends(RateLimiter(requests_limit=1, time_window=10))],
)
def register_team(
    team_create: TeamCreate, session: Annotated[Session, Depends(get_session)]
) -> dict[str, str]:
    try:
        session.exec(
            select(Team).where(Team.team_number == team_create.team_number)
        ).one()
    except Exception:
        pass
    else:
        raise HTTPException(status_code=HTTP_409_CONFLICT, detail="Team already exists")

    new_team_leader = team.get_user_from_username(session, team_create.leader_username)

    if new_team_leader is None:
        raise HTTPException(status_code=404, detail="User does not exist")

    try:
        session.exec(select(Team).where(Team.leader_user == new_team_leader.id)).one()
    except Exception:
        pass
    else:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail="Leader already leads another team"
        )

    try:
        team.create(session, team_create)
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add team to database",
        ) from None
    else:
        return {"detail": "Successfully registered team"}


@router.get("/logout", tags=["Auth"])
def logout() -> RedirectResponse:
    response = RedirectResponse(url="/login")
    response.delete_cookie("access_token")
    return response


@router.put("/rotate-key")
def rotate_api_key(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> str:
    key = generate_api_key()
    current_user.api_key = get_password_hash(key)
    session.add(user)
    session.commit()

    return key
