from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
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
    generate_verification_code,
    get_current_active_user,
    get_password_hash,
)
from app.core.helpers import get_user_from_username
from app.db.database import get_session
from app.models.models import NewTeamData, NewUserData
from app.models.schemas import Team, User
from app.services.email.email import send_verification_email

router = APIRouter()

@router.post("/token", dependencies=[Depends(RateLimiter(requests_limit=10, time_window=5))])
def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)]
):

    user = authenticate_user(session=session, username=form_data.username, password=form_data.password) # type: ignore
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

@router.get("/users/me", dependencies=[Depends(RateLimiter(requests_limit=10, time_window=5))])
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user

@router.post("/register", dependencies=[Depends(RateLimiter(requests_limit=1, time_window=10))])
def register_user(
    new_user: NewUserData,
    session: Annotated[Session, Depends(get_session)]
):
    if new_user.team:
        try:
            session.exec(select(Team).where(Team.team_number == new_user.team)).one()
        except Exception:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="Team does not exist"
            )
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
        session.exec(select(User).where(User.username == new_user.email)).one()
    except Exception:
        pass
    else:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail="Username is taken"
        )

    try:
        user = User(
            username=new_user.username,
            email=new_user.email,
            password=get_password_hash(new_user.password),
            team=new_user.team,
            code=generate_verification_code(session)
        )
        session.add(user)
    except:
        session.rollback()
        raise
    else:
        session.commit()
        send_verification_email(user)

@router.get("/verify", dependencies=[Depends(RateLimiter(requests_limit=2, time_window=10))])
def verify_email_code(
    code: str,
    session: Annotated[Session, Depends(get_session)]
):
    try:
        user = session.exec(select(User).where(User.code == code)).one()

    except Exception:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Incorrect Verification Code"
        )

    try:
        user.code = None
        user.disabled = False
        session.add(user)
    except Exception:
        session.rollback()
    else:
        session.commit()

@router.post("/register/team", dependencies=[Depends(RateLimiter(requests_limit=1, time_window=10))])
def register_team(
    new_team: Annotated[NewTeamData, Query()],
    session: Annotated[Session, Depends(get_session)]
):
    try:
        session.exec(select(Team).where(Team.team_number == new_team.team_number)).one()
    except Exception:
        pass
    else:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail="Team already exists"
        )

    new_team_leader = get_user_from_username(new_team.leader_username, session)
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
        team = Team(
            team_number=new_team.team_number,
            team_name=new_team.team_name,
            leader_user=new_team_leader.id
        )
        session.add(team)
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add team to database"
        )
    else:
        session.commit()

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie("access_token")
    return response
