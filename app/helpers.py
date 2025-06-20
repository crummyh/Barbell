
from sqlmodel import Session, select

from app.models import Team


def get_team_from_id(id: int, session: Session) -> Team:
    """
    Returns the `Team` that corresponds to the `id`. Basically just does `session.get()`
    """
    team = session.get(Team, id)
    if not team:
        raise LookupError()
    return team

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
    Returns the internal db id of a team based off of its team number
    """
    team = session.exec(select(Team).where(Team.team_number == team_number)).one_or_none()
    if not team:
        raise LookupError()
    return team
