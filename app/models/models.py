from enum import Enum
from typing import IO, Any, Dict, Optional

from fastapi import Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr
from pydantic.types import UUID4

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
    team_count: int
    # years_available: list[int]
    # labels: dict[str, list[str]]
    # uptime: str

class TeamStatsOut(BaseModel):
    image_count: int
    years_available: set[int]
    upload_batches: int

class StatusOut(BaseModel):
    batch_id: UUID4
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

class ReviewMetadata(BaseModel):
    id: str
    labels: Dict[str, Any]

class NewUserData(BaseModel):
    username: str
    email: EmailStr
    password: str
    team: Optional[int] = None

def image_response(file: IO[bytes]) -> Response:
    file.seek(0)
    return StreamingResponse(
        file,
        media_type="image",
        headers={
            "Content-Disposition": "attachment"
        }
    )
# ==========={ Security }=========== #

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None
