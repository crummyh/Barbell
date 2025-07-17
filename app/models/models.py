from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum
from typing import IO, TYPE_CHECKING, List, Optional
from uuid import UUID

from fastapi import Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr

if TYPE_CHECKING:
    from app.models.schemas import Annotation

# ==========={ Enums & States }=========== #

class UploadStatus(Enum):
    UPLOADING  = "uploading"
    PROCESSING = "processing"
    COMPLETED  = "completed"
    FAILED     = "failed"

class DownloadFormat(Enum):
    YOLO5  = "yolo5"
    YOLO8  = "yolo8"
    YOLO11 = "yolo11"
    COCO   = "coco"
    RAW    = "raw"

class UserRole(Enum):
    DEFAULT     = 0
    TEAM_LEADER = 1
    MODERATOR   = 2
    ADMIN       = 3

# ==========={ Responses }=========== #

class StatsOut(BaseModel):
    image_count: int
    un_reviewed_image_count: int
    team_count: int
    # years_available: list[int]
    # labels: dict[str, list[str]]
    uptime: timedelta

class TeamStatsOut(BaseModel):
    image_count: int
    un_reviewed_image_count: int
    years_available: set[int]
    upload_batches: int

class StatusOut(BaseModel):
    batch_id: UUID
    team: int
    status: UploadStatus
    file_size: Optional[int]
    images_valid: Optional[int]
    images_rejected: Optional[int]
    images_total: Optional[int]
    estimated_time_left: Optional[float]
    error_msg: Optional[str]

# ==========={ Requests }=========== #

class DownloadRequest(BaseModel):
    format: DownloadFormat
    labels: list[str]
    count: tuple[int, int, int] | int # Training / Validation / Testing | Number
    non_match_images: bool

class NewUserData(BaseModel):
    username: str
    email: EmailStr
    password: str
    team: Optional[int] = None

class NewTeamData(BaseModel):
    team_number: int
    team_name: str
    leader_username: str

def image_response(file: IO[bytes]) -> Response:
    file.seek(0)
    return StreamingResponse(
        file,
        media_type="image",
        headers={
            "Content-Disposition": "attachment"
        }
    )

# ==========={ Responses and Requests }=========== #

class ReviewMetadata(BaseModel):
    id: UUID
    annotations: Optional[List[Annotation]]
    created_at: datetime
    created_by: int
    batch: UUID
    reviewed: bool

# ==========={ Security }=========== #

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None
