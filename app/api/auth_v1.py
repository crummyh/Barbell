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
    authenticate_user,
    create_access_token,
    get_current_active_user,
)
from app.crud import team, user
from app.database import get_session
from app.models.models import Team, TeamCreate, User, UserCreate, UserUpdate
from app.services.email.email import send_verification_email

router = APIRouter()

@router.post("/token", tags=["Auth"], dependencies=[Depends(RateLimiter(requests_limit=10, time_window=5))])
def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)]
):

    user = authenticate_user(session=session, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.name}, expires_delta=access_token_expires
    )

    resp = JSONResponse(content={"message": "Login successful"})
    resp.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=config.IS_PRODUCTION,
        samesite="lax",
        max_age=60*60*24
    )

    return resp

@router.get("/users/me", tags=["Auth"], dependencies=[Depends(RateLimiter(requests_limit=10, time_window=5))])
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user.get_public()

@router.post("/register", tags=["Auth"], dependencies=[Depends(RateLimiter(requests_limit=1, time_window=10))])
def register_user(
    new_user: UserCreate,
    background_tasks: BackgroundTasks,
    session: Annotated[Session, Depends(get_session)]
):
    try:
        session.exec(select(User).where(User.email == new_user.email)).one()
    except Exception:
        pass
    else:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail="Email is taken"
        )

    try:
        session.exec(select(User).where(User.username == new_user.username)).one()
    except Exception:
        pass
    else:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail="Username is taken"
        )

    try:
        db_user = user.create(session, new_user)
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    else:
        background_tasks.add(send_verification_email, db_user)
        return {"detail": "Successfully registered"}

@router.get("/verify", tags=["Auth"], dependencies=[Depends(RateLimiter(requests_limit=2, time_window=10))])
def verify_email_code(
    code: str,
    session: Annotated[Session, Depends(get_session)]
):
    try:
        db_user = session.exec(select(User).where(User.code == code)).one()

    except Exception:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Incorrect Verification Code"
        )

    try:
        user.update(session, db_user.id, {"code"=None, "disabled"=False})

    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to modify user"
        )
    else:
        return {"detail": "Successfully verified"}

@router.post("/register/team", tags=["Auth"], dependencies=[Depends(RateLimiter(requests_limit=1, time_window=10))])
def register_team(
    team_create: TeamCreate,
    session: Annotated[Session, Depends(get_session)]
):
    try:
        session.exec(select(Team).where(Team.team_number == team_create.team_number)).one()
    except Exception:
        pass
    else:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail="Team already exists"
        )

    new_team_leader = team.get_user_from_username(session, team_create.leader_username)
    try:
        session.exec(select(Team).where(Team.leader_user == new_team_leader.id)).one()
    except Exception:
        pass
    else:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail="Leader already leads another team"
        )

    try:
        team.create(session, team_create)
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add team to database"
        )
    else:
        return {"detail": "Successfully registered team"}

@router.get("/logout", tags=["Auth"])
def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie("access_token")
    return response
