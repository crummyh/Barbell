import tarfile
from datetime import datetime, timezone
from typing import Annotated, Sequence

from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile
from fastapi.exceptions import HTTPException
from pydantic.types import UUID4
from sqlalchemy import func
from sqlmodel import Session, select
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

from app.core import config
from app.core.dependencies import (
    RateLimiter,
    generate_api_key,
    get_password_hash,
    handle_api_key,
)
from app.core.helpers import (
    get_hash_with_streaming,
    get_id_from_team_number,
    get_team_from_id,
    get_team_number_from_id,
)
from app.db.database import get_session
from app.models.models import (
    DownloadRequest,
    DownloadStatus,
    DownloadStatusOut,
    ImageReviewStatus,
    StatsOut,
    TeamStatsOut,
    UploadStatus,
    UploadStatusOut,
)
from app.models.schemas import (
    DownloadBatch,
    Image,
    LabelSuperCategory,
    Team,
    UploadBatch,
)
from app.services.buckets import create_upload_batch
from app.services.monitoring import get_uptime
from app.tasks.download_packaging import create_download_batch
from app.tasks.image_processing import estimate_processing_time, process_batch_async

router = APIRouter()

# ========== { Public API } ========== #

@router.get("/stats", tags=["Public", "Stats"], dependencies=[Depends(RateLimiter(requests_limit=20, time_window=10))])
def get_stats(session: Annotated[Session, Depends(get_session)]) -> StatsOut:
    """
    Get stats about the entire database
    """
    out = StatsOut(
        image_count=session.exec(select(func.count()).select_from(Image)).one(),
        un_reviewed_image_count=session.exec(select(func.count()).select_from(Image).where(Image.review_status != ImageReviewStatus.APPROVED)).one(),
        team_count=session.exec(select(func.count()).select_from(Team)).one(),
        uptime=get_uptime()
    )
    return out

@router.get("/stats/team/{team_number}", tags=["Public", "Stats"], dependencies=[Depends(RateLimiter(requests_limit=10, time_window=10))])
def get_team_stats(team_number: int, session: Annotated[Session, Depends(get_session)]) -> TeamStatsOut:
    """
    Get stats about individual teams

    - **team_number**: The team to look at
    """

    try:
        team = get_id_from_team_number(team_number, session)
    except LookupError:
        raise HTTPException(status_code=404, detail="Team not found")

    images = session.exec(select(Image).where(Image.created_by == team).where(Image.review_status == ImageReviewStatus.APPROVED)).all()
    pre_images = session.exec(select(Image).where(Image.created_by == team).where(Image.review_status != ImageReviewStatus.APPROVED)).all()
    batches = session.exec(select(UploadBatch).where(UploadBatch.team == team)).all()

    out = TeamStatsOut(
        image_count=len(images),
        un_reviewed_image_count=len(pre_images),
        years_available=set([i.created_at.year for i in images]),
        upload_batches=len(batches)
    )
    return out

@router.get("/stats/labels")
def get_label_info(
    session: Annotated[Session, Depends(get_session)]
) -> Sequence[LabelSuperCategory]:
    categories = session.exec(select(LabelSuperCategory)).all()

    if not categories:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="No categories found"
        )

    return categories

# ========== { Auth API } ========== #

@router.get("/status/{batch_id}", tags=["Auth Required",  "Stats"], dependencies=[Depends(RateLimiter(requests_limit=30, time_window=10))])
def get_batch_status(
    batch_id: UUID4,
    team: Annotated[Team, Depends(handle_api_key)],
    session: Annotated[Session, Depends(get_session)]
) -> UploadStatusOut:

    batch = session.get(UploadBatch, batch_id)
    if not batch:
        raise HTTPException(
            status_code=404,
            detail="Batch not found"
        )

    out = UploadStatusOut(
        batch_id=batch_id,
        team=get_team_number_from_id(batch.team, session),
        status=batch.status,
        file_size=batch.file_size,
        images_valid=batch.images_valid,
        images_rejected=batch.images_rejected,
        images_total=batch.images_total,
        estimated_time_left=estimate_processing_time(session,batch_id),
        error_msg=batch.error_message
    )
    return out

@router.post("/upload", tags=["Auth Required"], dependencies=[Depends(RateLimiter(requests_limit=2, time_window=60))])
def upload(
    archive:          UploadFile,
    hash:             str,
    background_tasks: BackgroundTasks,
    team: Annotated[Team, Depends(handle_api_key)],
    session: Annotated[Session, Depends(get_session)],
    capture_time:     datetime = datetime.now(timezone.utc)
) -> UploadStatusOut:
    """
    Upload images to the dataset. Requires and API key

    `archive`: The images in a .tar.gz archive

    `hash`: A ***md5*** hash of the archive

    `capture_time`: The rough time that the data was gathered
    """

    if not tarfile.is_tarfile(archive.file):
        raise HTTPException(
            status_code=415,
            detail="File must be of type .tar.gz"
        )

    if archive.size and (archive.size > config.MAX_FILE_SIZE):
        raise HTTPException(
            status_code=413,
            detail=f"File is too large. Max size: {config.MAX_FILE_SIZE / (1024**3):.1f}GB"
        )

    if get_hash_with_streaming(archive.file, config.UPLOAD_INTEGRITY_HASH_ALGORITHM) != hash:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is corrupted (hash mismatch) (Are you using md5?)"
        )

    try:
        assert team.id
        batch = UploadBatch(
            team=team.id,
            status=UploadStatus.UPLOADING,
            file_size=archive.size,
            capture_time=capture_time
        )
        session.add(batch)
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail="There was an error adding the batch to the database. Sorry!"
        )
    else:
        session.commit()

        try:
            assert batch.id
            create_upload_batch(archive.file, batch.id)

        except Exception:
            raise HTTPException(
                status_code=500,
                detail="There was an error creating a S3 object"
            )

        else:
            background_tasks.add_task(process_batch_async, batch_id=batch.id)

    return UploadStatusOut(
        batch_id=batch.id,
        team=get_team_from_id(team.id, session).team_number,
        status=UploadStatus.PROCESSING,
        file_size=archive.size,
        images_valid=None,
        images_total=None,
        images_rejected=None,
        estimated_time_left=config.DEFAULT_PROCESSING_TIME,
        error_msg=None
    )

@router.get("/download", tags=["Auth Required"], dependencies=[Depends(RateLimiter(requests_limit=1, time_window=60))])
def download_batch(
    request: DownloadRequest,
    background_tasks: BackgroundTasks,
    team: Annotated[Team, Depends(handle_api_key)],
    session: Annotated[Session, Depends(get_session)]
) -> DownloadStatusOut:
    try:
        assert team.id
        batch = DownloadBatch(
            team=team.id,
            status=DownloadStatus.STARTING,
            non_match_images=request.non_match_images,
            image_count=request.count,
            annotations=request.annotations
        )
        session.add(batch)
        session.commit()
        session.flush()
        assert batch.id

    except Exception:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add batch to database"
        )

    else:
        background_tasks.add_task(create_download_batch, batch_id=batch.id)
        return DownloadStatusOut(
            id=batch.id,
            team=batch.team,
            status=batch.status,
            file_size=batch.file_size,
            non_match_images=batch.non_match_images,
            image_count=batch.image_count,
            annotations=batch.annotations,
            start_time=batch.start_time,
            estimated_processing_time_left=batch.estimated_processing_time_left,
            hash=batch.hash,
            error_message=batch.error_message
        )

# ==========={ Management }=========== #

@router.put("/rotate-key", dependencies=[Depends(RateLimiter(requests_limit=1, time_window=60))])
def rotate_api_key(
    team: Annotated[Team, Depends(handle_api_key)],
    session: Annotated[Session, Depends(get_session)]
):
    try:
        team.api_key = get_password_hash(generate_api_key())
        session.add(team)
    except Exception:
        session.rollback()
    else:
        session.commit()

    session.refresh(team)
    return team.api_key
