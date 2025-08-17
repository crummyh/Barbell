import time
from datetime import datetime, timedelta, timezone
from secrets import token_hex, token_urlsafe
from typing import Annotated, AsyncGenerator, Optional

import jwt
from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from sqlmodel import Session, select

from app.core import config
from app.db.database import get_session
from app.models.models import TokenData, UserRole
from app.models.schemas import Team, User

# ==========={ Database }=========== #

SessionDep = Annotated[Session, Depends(get_session)]

# ==========={ Security }=========== #

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==========={ API Keys }=========== #

# Combines a key and team number:
# {KEY}:{TEAM NUMBER}
api_auth_scheme = APIKeyHeader(name="x-api-auth", auto_error=False)

async def handle_api_key(
    db: SessionDep,
    token: str = Security(api_auth_scheme)
) -> AsyncGenerator[Team, None]:
    try:
        key_id, key = token.split(":", 1)

        res = db.exec(select(Team).where(Team.team_number == int(key_id)).where(Team.disabled == False))  # noqa: E712
        team = res.one()

        if not pwd_context.verify(key, team.api_key):
            raise Exception("Invalid API key")

        yield team

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )

def generate_api_key() -> str:
    return token_hex(config.API_KEY_LEN)

# ==========={ Passwords }=========== #

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

async def get_token_from_cookie(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return token

async def optional_auth(request: Request) -> Optional[str]:
    try:
        return await get_token_from_cookie(request)
    except HTTPException:
        return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def authenticate_user(
    session: Annotated[Session, Depends(get_session)],
    username: str,
    password: str
) -> Optional[User]:
    user = session.exec(select(User).where(User.username == username)).one_or_none()
    if not user:
        user = session.exec(select(User).where(User.email == username)).one_or_none()
        if not user:
            return None
    assert user.password
    if not verify_password(password, user.password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        config.JWT_SECRET_TOKEN,
        algorithm=config.SECURE_ALGORITHM
    )
    return encoded_jwt

def get_current_user(
    token: Annotated[Optional[str], Depends(optional_auth)],
    session: Annotated[Session, Depends(get_session)]
) -> Optional[User]:
    # credentials_exception = HTTPException(
    #     status_code=status.HTTP_401_UNAUTHORIZED,
    #     detail="Could not validate credentials",
    #     headers={"WWW-Authenticate": "Bearer"},
    # )
    try:
        payload = jwt.decode(
            token,
            config.JWT_SECRET_TOKEN,
            algorithms=[config.SECURE_ALGORITHM]
        )
        username = payload.get("sub")
        if username is None:
            return None

        token_data = TokenData(username=username)

    except InvalidTokenError:
        return None

    user = session.exec(select(User).where(User.username == token_data.username)).one_or_none()
    if user is None:
        return None

    return user

def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_login(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


def require_role(*roles: UserRole):
    def role_checker(user: User = Depends(get_current_active_user)):
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role: {[i.name for i in roles]}, but you have: {user.role.name}",
            )
        return user
    return role_checker

def minimum_role(role: UserRole):
    def role_checker(user: User = Depends(get_current_active_user)):
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if user.role.value <= role.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role: {role.name} or greater, but you have: {user.role.name}",
            )
        return user
    return role_checker

def generate_verification_code(
    session: Annotated[Session, Depends(get_session)]
) -> str:
    while True:
        code = token_urlsafe(config.VERIFICATION_CODE_BYTES_LEN)
        try:
           session.exec(select(User).where(User.code == code)).one()
        except Exception:
            return code

# ==========={ Rate Limiting }=========== #
#
request_counters = {}
class RateLimiter:
    def __init__(self, requests_limit: int, time_window: int):
        self.requests_limit = requests_limit
        self.time_window = time_window

    async def __call__(self, request: Request):
        assert request.client
        client_ip = request.client.host
        route_path = request.url.path

        # Get the current timestamp
        current_time = int(time.time())

        # Create a unique key based on client IP and route path
        key = f"{client_ip}:{route_path}"

        # Check if client's request counter exists
        if key not in request_counters:
            request_counters[key] = {"timestamp": current_time, "count": 1}
        else:
            # Check if the time window has elapsed, reset the counter if needed
            if current_time - request_counters[key]["timestamp"] > self.time_window:
                # Reset the counter and update the timestamp
                request_counters[key]["timestamp"] = current_time
                request_counters[key]["count"] = 1
            else:
                # Check if the client has exceeded the request limit
                if request_counters[key]["count"] >= self.requests_limit:
                    raise HTTPException(status_code=429, detail="Too Many Requests")
                else:
                    request_counters[key]["count"] += 1

        # Clean up expired client data
        for k in list(request_counters.keys()):
            if current_time - request_counters[k]["timestamp"] > self.time_window:
                request_counters.pop(k)

        return True
