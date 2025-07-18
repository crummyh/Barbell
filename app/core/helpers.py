
import hashlib
from typing import BinaryIO

from sqlalchemy import asc
from sqlmodel import Session, select

from app.core import config
from app.models.schemas import Image, Team, User


def get_team_from_id(id: int, session: Session) -> Team:
    """
    Returns the `Team` that corresponds to the `id`. Basically just does `session.get()`
    """
    team = session.get(Team, id)
    if not team:
        raise LookupError()
    return team

def get_team_number_from_id(id: int, session: Session) -> int:
    """
    Returns the team number that corresponds to the `id`
    """
    return get_team_from_id(id, session).team_number

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

def get_hash_with_streaming(file: BinaryIO, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    file.seek(0)
    while True:
        data = file.read(config.HASHING_BUF_SIZE)
        if not data:
            break
        h.update(data)

    return h.hexdigest()

def get_un_reviewed_img_labeled(session: Session) -> Image:
    statement = (
        select(Image).where(Image.annotations != [])  # noqa: E711
        .order_by(asc(Image.created_at)) # type: ignore
        .limit(1)
    )
    image = session.exec(statement).one()
    if not image:
        raise LookupError()
    return image

def get_un_reviewed_img(session: Session) -> Image:
    statement = (
        select(Image)
        .order_by(asc(Image.created_at)) # type: ignore
        .limit(1)
    )
    image = session.exec(statement).one()
    if not image:
        raise LookupError()
    return image

def get_user_from_username(username: str, session: Session) -> User:
    return session.exec(select(User).where(User.username == username)).one()
