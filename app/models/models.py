from __future__ import annotations

from datetime import timedelta
from typing import BinaryIO

from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.models.user import UserRole

# ==========={ Guild }=========== #
"""
A guild for separating schemas:
`___Base`: Common fields
`___`: db/internal only fields
`___Create`: Fields that are not controlled by the database and needed
`___Public`: Fields that need to be accessed, but need a different definition then in the db
"""

# ==========={ Responses }=========== #


class StatsOut(BaseModel):
    image_count: int
    un_reviewed_image_count: int
    team_count: int
    uptime: timedelta


class TeamStatsOut(BaseModel):
    image_count: int
    un_reviewed_image_count: int
    years_available: set[int]
    upload_batches: int


def image_response(file: BinaryIO) -> StreamingResponse:
    file.seek(0)
    return StreamingResponse(
        file, media_type="image", headers={"Content-Disposition": "attachment"}
    )


# ==========={ Requests }=========== #


class RateLimitUpdate(BaseModel):
    route: str
    requests_limit: int
    time_window: int


# ==========={ Security }=========== #


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    role: UserRole | None = None
