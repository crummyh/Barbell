import time
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from secrets import token_hex, token_urlsafe
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from sqlmodel import Session, or_, select

from app.core import config
from app.database import get_session
from app.models.user import User, UserRole

# ==========={ Database }=========== #

SessionDep = Annotated[Session, Depends(get_session)]

# ==========={ Security }=========== #

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    hash: str = pwd_context.hash(password)
    return hash


# ==========={ API Keys }=========== #

api_auth_scheme = APIKeyHeader(name="x-api-auth", auto_error=False)


async def handle_api_key(
    db: SessionDep, token: str | None = Security(api_auth_scheme)
) -> User | None:
    if not token:
        return None

    try:
        parts = token.split(":", 1)
        if len(parts) != 2:
            return None

        username, key = parts
        if not username or not key:
            return None

        user: User | None = db.exec(
            select(User).where(
                User.username == username,
                User.disabled == False,  # noqa: E712
                User.api_key != None,  # noqa: E711
            )
        ).one_or_none()

        if not user or not user.api_key:
            return None

        if not pwd_context.verify(key, user.api_key):
            return None

        return user

    except Exception:
        return None


def generate_api_key() -> str:
    return token_hex(config.API_KEY_LEN)


# ==========={ JWT }=========== #


async def handle_jwt(
    request: Request,
    session: SessionDep,
) -> User | None:
    token = request.cookies.get("access_token")
    if not token:
        return None

    try:
        payload = jwt.decode(
            token, config.JWT_SECRET_TOKEN, algorithms=[config.SECURE_ALGORITHM]
        )
        username = payload.get("sub")
        if not username:
            return None

        user: User | None = session.exec(
            select(User).where(
                User.username == username,
                User.disabled == False,  # noqa: E712
            )
        ).one_or_none()

        return user

    except InvalidTokenError:
        return None
    except Exception:
        return None


def handle_raw_auth(session: SessionDep, username: str, password: str) -> User | None:
    """Handle username/password authentication"""
    if not username or not password:
        return None

    user: User | None = session.exec(
        select(User).where(
            or_(User.username == username, User.email == username),
            User.disabled == False,  # noqa: E712
            User.password != None,  # noqa: E711
        )
    ).one_or_none()

    if not user or not user.password:
        return None

    if not pwd_context.verify(password, user.password):
        return None

    return user


def create_access_token(
    data: dict, expires_delta: timedelta = timedelta(minutes=15)
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(
        to_encode, config.JWT_SECRET_TOKEN, algorithm=config.SECURE_ALGORITHM
    )
    return encoded_jwt


# ==========={ Common }=========== #


# Consider adding type hints for the Security dependencies
async def get_current_user_optional(
    db: SessionDep,
    request: Request,
) -> User | None:
    """Try multiple authentication methods in order of preference"""

    if api_user := await handle_api_key(db, request.headers.get("x-api-auth")):
        return api_user

    if jwt_user := await handle_jwt(request, db):
        return jwt_user

    return None


async def get_current_user(
    user: Annotated[User | None, Depends(get_current_user_optional)],
) -> User:
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Use API key or login session.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# ==========={ Additional Utilities }=========== #


async def get_api_user_only(
    db: SessionDep, token: str = Security(api_auth_scheme)
) -> User:
    user = await handle_api_key(db, token)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Valid API key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return user


async def get_web_user_only_optional(
    request: Request,
    session: SessionDep,
) -> User | None:
    user = await handle_jwt(request, session)
    return user


async def get_web_user_only(
    request: Request,
    session: SessionDep,
) -> User:
    user = await handle_jwt(request, session)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Please log in to continue",
        )
    return user


def require_role(*roles: UserRole) -> Callable[[User], User]:
    def role_checker(user: User = Depends(get_current_user)) -> User:
        if not user.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User role not assigned",
            )

        if user.role not in roles:
            role_names = [role.name for role in roles]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {', '.join(role_names)}. Your role: {user.role.name}",
            )

        return user

    return role_checker


def minimum_role(min_role: UserRole) -> Callable[[User], User]:
    def role_checker(user: User = Depends(get_current_user)) -> User:
        if not user.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User role not assigned",
            )

        if user.role.value < min_role.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {min_role.name} or higher. Your role: {user.role.name}",
            )

        return user

    return role_checker


def generate_verification_code(
    session: Annotated[Session, Depends(get_session)],
) -> str:
    while True:
        code = token_urlsafe(config.VERIFICATION_CODE_BYTES_LEN)
        try:
            session.exec(select(User).where(User.code == code)).one()
        except Exception:
            return code


# ==========={ Rate Limiting }=========== #

request_counters = {}

rate_limit_config: dict[str, dict[str, int]] = {}


class RateLimiter:
    def __init__(self, requests_limit: int = 30, time_window: int = 10):
        self.default_requests = requests_limit
        self.default_window = time_window

    async def __call__(self, request: Request) -> bool:
        assert request.client
        client_ip = request.client.host
        route_path = request.url.path  # full request path

        current_time = int(time.time())
        key = f"{client_ip}:{route_path}"

        # Look up per-endpoint config, fallback to defaults
        cfg = rate_limit_config.get(
            route_path,
            {
                "requests_limit": self.default_requests,
                "time_window": self.default_window,
            },
        )
        requests_limit = cfg["requests_limit"]
        time_window = cfg["time_window"]

        # Track requests
        if key not in request_counters:
            request_counters[key] = {"timestamp": current_time, "count": 1}
        else:
            if current_time - request_counters[key]["timestamp"] > time_window:
                request_counters[key] = {"timestamp": current_time, "count": 1}
            else:
                if request_counters[key]["count"] >= requests_limit:
                    raise HTTPException(status_code=429, detail="Too Many Requests")
                request_counters[key]["count"] += 1

        # Cleanup old entries
        for k in list(request_counters.keys()):
            if current_time - request_counters[k]["timestamp"] > time_window:
                request_counters.pop(k)

        return True
