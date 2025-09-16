from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from app.core import config

if TYPE_CHECKING:
    from app.models.download_batch import DownloadBatch
    from app.models.team import Team
    from app.models.upload_batch import UploadBatch

class UserRole(int, Enum):
    DEFAULT     = 0
    TEAM_LEADER = 1
    MODERATOR   = 2
    ADMIN       = 3

class UserBase(SQLModel):
    username: str = Field(index=True, max_length=config.MAX_USERNAME_LEN, min_length=config.MIN_USERNAME_LEN)
    email: EmailStr = Field(unique=True)

class User(UserBase, table=True):
    __tablename__ = "users" # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    disabled: Optional[bool] = Field(default=True)
    api_key: Optional[str] = Field(default=None, index=True, unique=True)
    password: str = Field(max_length=config.MAX_PASSWORD_LENGTH, min_length=config.MIN_PASSWORD_LENGTH)
    role: Optional["UserRole"] = Field(default=UserRole.DEFAULT)
    code: Optional[str] = Field(default=None, max_length=config.VERIFICATION_CODE_STR_LEN)

    led_team: Optional["Team"] = Relationship(back_populates="leader")
    upload_batches: List["UploadBatch"] = Relationship(back_populates="user")
    download_batches: List["DownloadBatch"] = Relationship(back_populates="user")

    def get_public(self) -> "UserPublic":
        public = UserPublic.model_validate(self)
        if self.led_team:
            public.team = self.led_team.team_number

        return public

class UserCreate(UserBase):
    password: str

class UserUpdate(SQLModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = Field(
        default=None,
        max_length=config.MAX_PASSWORD_LENGTH,
        min_length=config.MIN_PASSWORD_LENGTH,
    )
    disabled: bool | None = None
    team: int | None = None
    role: UserRole | None = None
    code: str | None = None

class UserPublic(UserBase):
    id: int
    created_at: datetime
    disabled: bool
    role: UserRole
    team: int | None
