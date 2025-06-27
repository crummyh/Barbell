import hashlib
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlmodel import Session, select

from app.db.database import get_session
from app.models.schemas import Team

api_key_scheme = APIKeyHeader(name="x-api-key")
limiter = Limiter(key_func=get_remote_address)

SessionDep = Annotated[Session, Depends(get_session)]

def hash_key(api_key: str):
    return hashlib.sha256(api_key.encode()).hexdigest()

def check_api_key(api_key: str, session: SessionDep) -> int:
    hash = hash_key(api_key)
    teams = session.exec(select(Team)).all()
    teams = {t.api_key: t.id for t in teams}
    if hash in teams.keys():
        assert teams[hash] is not None
        return teams[hash] # type: ignore
    else:
        raise HTTPException(status_code=401, detail="Missing or invalid API key")
