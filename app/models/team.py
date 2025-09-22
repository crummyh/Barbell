from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.core import config
from app.core.helpers import validated

if TYPE_CHECKING:
    from app.models.user import User


class TeamBase(SQLModel):
    team_number: int = Field(index=True, unique=True, ge=0, le=config.MAX_TEAM_NUMB)
    team_name: str = Field(max_length=config.MAX_TEAM_NAME_LEN)


class Team(TeamBase, table=True):
    __tablename__ = "teams"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    disabled: bool = Field(default=False)
    leader_user: int | None = Field(
        default=None, foreign_key="users.id", unique=True, index=True
    )

    leader: Optional["User"] = Relationship(back_populates="led_team")

    def get_public(self) -> "TeamPublic":
        return validated(TeamPublic, self)


class TeamCreate(SQLModel):
    team_number: int
    team_name: str
    leader_username: str


class TeamUpdate(SQLModel):
    team_number: int | None = None
    team_name: str | None = None
    leader_username: str | None = None


class TeamPublic(TeamBase):
    id: int
    created_at: datetime
    disabled: bool
