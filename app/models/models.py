from enum import Enum
from typing import IO

from fastapi import Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pydantic.types import UUID4
from sqlmodel import JSON

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
    file_size: int | None
    images_valid: int | None
    images_rejected: int | None
    images_total: int | None
    estimated_time_left: float | None
    error_msg: str | None

class DownloadRequest(BaseModel):
    format: DownloadFormat
    labels: list[str]
    count: tuple[int, int, int] | int # Training / Validation / Testing | Number
    non_match_images: bool

class ReviewMetadata(BaseModel):
    id: str
    labels: JSON

def image_response(file: IO[bytes]) -> Response:
    file.seek(0)
    return StreamingResponse(
        file,
        media_type="image",
        headers={
            "Content-Disposition": "attachment"
        }
    )
