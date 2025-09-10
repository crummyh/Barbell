
import hashlib
import json
from typing import BinaryIO
from uuid import UUID

from sqlmodel import Session, select

from app.core import config
from app.models.schemas import Team, User


def get_team_from_id(id: int, session: Session) -> Team:
    """
    Returns the `Team` that corresponds to the `id`. Basically just does `session.get()`
    """
    team = session.get(Team, id)
    if not team:
        raise LookupError()
    return team

def get_team_number_from_id(id: int | None, session: Session) -> int:
    """
    Returns the team number that corresponds to the `id`
    """
    if id is None:
        return 0
    try:
        return get_team_from_id(id, session).team_number
    except LookupError:
        return 0

def get_id_from_team_number(team_number: int, session: Session) -> int:
    """
    Returns the internal db id of a team based off of its team number
    """
    team = session.exec(select(Team).where(Team.team_number == team_number)).one_or_none()
    if not team:
        raise LookupError()
    assert team.id is not None
    return team.id

def get_team_from_number(team_number: int, session: Session) -> Team:
    """
    Returns the `Team` object corresponding to an actual team number
    """
    team = session.exec(select(Team).where(Team.team_number == team_number)).one_or_none()
    if not team:
        raise LookupError()
    return team

def get_username_from_id(user_id: int, session: Session) -> str:
    try:
        username = session.get(User, user_id).username
        return username
    except Exception:
        raise LookupError()

def get_hash_with_streaming(file: BinaryIO, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    file.seek(0)
    while True:
        data = file.read(config.HASHING_BUF_SIZE)
        if not data:
            break
        h.update(data)

    return h.hexdigest()

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)
