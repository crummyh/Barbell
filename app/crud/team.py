from sqlmodel import Session, select

from app.crud.user import get_user_from_username
from app.models.team import Team, TeamCreate, TeamUpdate


def create(session: Session, team_create: TeamCreate) -> Team:
    team: Team = Team.model_validate(team_create)
    leader = get_user_from_username(session, team_create.leader_username)
    assert leader
    team.leader_user = leader.id

    session.add(team)
    session.commit()
    session.refresh(team)
    return team


def get(session: Session, id: int) -> Team | None:
    team: Team | None = session.get(Team, id)
    return team


def get_from_number(session: Session, number: int) -> Team | None:
    team = session.exec(select(Team).where(Team.team_number == number)).one_or_none()

    assert isinstance(team, Team) or team is None
    return team


def update(session: Session, id: int, team_update: TeamUpdate | dict) -> Team | None:
    team: Team | None = session.get(Team, id)
    if team is None:
        return None

    if isinstance(team_update, dict):
        team_update = TeamUpdate(**team_update)

    new_team_data = team_update.model_dump(exclude_unset=True)
    team.sqlmodel_update(new_team_data)
    session.add(team)
    session.commit()
    session.refresh(team)

    assert isinstance(team, Team) or team is None
    return team


def delete(session: Session, id: int) -> bool:
    team = session.get(Team, id)
    if team is None:
        return False

    session.delete(team)
    session.commit()
    return True
