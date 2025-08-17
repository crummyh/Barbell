from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum
from typing import BinaryIO, Dict, List, Optional
from uuid import UUID

from fastapi import Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr

# ==========={ Enums & States }=========== #

class UploadStatus(Enum):
    UPLOADING  = "uploading"
    PROCESSING = "processing"
    COMPLETED  = "completed"
    FAILED     = "failed"

class DownloadStatus(Enum):
    STARTING = "starting"
    ASSEMBLING_LABELS = "assembling_labels"
    ASSEMBLING_IMAGES = "assembling_images"
    ADDING_MANIFEST = "adding_manifest"
    READY = "ready"
    FAILED = "failed"

class UserRole(Enum):
    DEFAULT     = 0
    TEAM_LEADER = 1
    MODERATOR   = 2
    ADMIN       = 3

class ImageReviewStatus(Enum):
    APPROVED = "approved"
    AWAITING_LABELS = "awaiting_labels"
    NOT_REVIEWED = "not_reviewed"

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

class UploadStatusOut(BaseModel):
    batch_id: UUID
    team: int
    status: UploadStatus
    file_size: Optional[int]
    images_valid: Optional[int]
    images_rejected: Optional[int]
    images_total: Optional[int]
    estimated_time_left: Optional[float]
    error_msg: Optional[str]

class DownloadStatusOut(BaseModel):
    id: UUID | None
    team: int
    status: DownloadStatus
    non_match_images: bool
    image_count: int | None
    annotations: Dict[str, bool | Dict[str, bool]]
    start_time: datetime
    hash: str | None
    error_message: str | None

class UserOut(BaseModel):
    username: str
    email: EmailStr | None
    disabled: bool
    created_at: datetime
    team_number: int
    role: UserRole

# ==========={ Requests }=========== #

class DownloadRequest(BaseModel):
    annotations: Dict[str, Dict[str, bool] | bool]
    count: int
    non_match_images: bool = True

class NewUserData(BaseModel):
    username: str
    email: EmailStr
    password: str
    team: Optional[int] = None

class NewTeamData(BaseModel):
    team_number: int
    team_name: str
    leader_username: str

def image_response(file: BinaryIO) -> Response:
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
    annotations: List["Annotation"] # Use [] for None
    created_at: datetime
    created_by: int
    batch: UUID
    review_status: ImageReviewStatus

# ==========={ Security }=========== #

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None

# I'm sorry
from app.models.schemas import Annotation  # noqa: E402

ReviewMetadata.model_rebuild()
