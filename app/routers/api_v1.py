import tarfile
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile
from fastapi.exceptions import HTTPException
from pydantic.types import UUID4
from sqlalchemy import func
from sqlmodel import Session, select

from app.buckets import create_upload_batch
from app.helpers import (
    get_hash_with_streaming,
    get_id_from_team_number,
    get_team_from_id,
    get_team_number_from_id,
)
from app.services.image_processing import estimate_processing_time, process_batch_async

from .. import config
from ..database import get_session
from ..dependencies import api_key_scheme, check_api_key
from ..models import (
    Image,
    StatsOut,
    StatusOut,
    Team,
    TeamStatsOut,
    UploadBatch,
    UploadStatus,
)

router = APIRouter()

# ========== { Public API } ==========

@router.get("/stats", tags=["Public", "Stats"])
def get_stats(session: Session = Depends(get_session)) -> StatsOut:
    """
    Get stats about the entire database
    """
    out = StatsOut(
        image_count=session.exec(select(func.count()).select_from(Image)).one(),
        team_count=session.exec(select(func.count()).select_from(Team)).one()
    )
    return out

@router.get("/stats/team/{team_number}", tags=["Public", "Stats"])
def get_team_stats(team_number: int, session: Session = Depends(get_session)) -> TeamStatsOut:
    """
    Get stats about individual teams

    - **team_number**: The team to look at
    """

    try:
        team = get_id_from_team_number(team_number, session)
    except LookupError:
        raise HTTPException(status_code=404, detail="Team not found")

    images = session.exec(select(Image).where(Image.created_by == team)).all()
    batches = session.exec(select(UploadBatch).where(UploadBatch.team_id == team)).all()

    out = TeamStatsOut(
        image_count=len(images),
        years_available=set([i.created_at.year for i in images]),
        upload_batches=len(batches)
    )
    return out

# ========== { Auth API } ==========

@router.get("/status/{batch_id}", tags=["Auth Required",  "Stats"])
def get_batch_status(
    batch_id: UUID4,
    api_key:  str     = Depends(api_key_scheme),
    session:  Session = Depends(get_session)
) -> StatusOut:
    check_api_key(api_key, session)

    batch = session.get(UploadBatch, batch_id)
    if not batch:
        raise HTTPException(
            status_code=404,
            detail="Batch not found"
        )

    out = StatusOut(
        batch_id=batch_id,
        team=get_team_number_from_id(batch.team_id, session),
        status=batch.status,
        file_size=batch.file_size,
        images_valid=batch.images_valid,
        images_rejected=batch.images_rejected,
        images_total=batch.images_total,
        estimated_time_left=estimate_processing_time(session,batch_id),
        error_msg=batch.error_message
    )
    return out

@router.post("/upload", tags=["Auth Required"])
def upload(
    archive:          UploadFile,
    hash:             str,
    background_tasks: BackgroundTasks,
    capture_time:     datetime = datetime.now(),
    api_key:          str      = Depends(api_key_scheme),
    session:          Session  = Depends(get_session)
) -> StatusOut:
    """
    Upload images to the dataset. Requires and API key

    `archive`: The images in a .tar.gz archive

    `hash`: A ***md5*** hash of the archive

    `capture_time`: The rough time that the data was gathered
    """
    team_id = check_api_key(api_key, session)

    if not tarfile.is_tarfile(archive.file):
        raise HTTPException(
            status_code=415,
            detail="File must be of type .tar.gz"
        )

    if archive.size and (archive.size > config.MAX_FILE_SIZE):
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size: {config.MAX_FILE_SIZE / (1024**3):.1f}GB"
        )

    if get_hash_with_streaming(archive.file, config.UPLOAD_INTEGRITY_HASH_ALGORITHM) != hash:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is corrupted (hash mismatch)."
        )

    try:
        batch = UploadBatch(
            team_id=team_id,
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
            background_tasks.add_task(process_batch_async, batch_id=batch.id, session=session)

    return StatusOut(
        batch_id=batch.id,
        team=get_team_from_id(team_id, session).team_number,
        status=UploadStatus.PROCESSING,
        file_size=archive.size,
        images_valid=None,
        images_total=None,
        images_rejected=None,
        estimated_time_left=config.DEFAULT_PROCESSING_TIME,
        error_msg=None
    )

@router.get("/download", tags=["Auth Required"])
def download_batch(
    api_key: str     = Depends(api_key_scheme),
    session: Session = Depends(get_session)
):
    team_id = check_api_key(api_key, session)
    pass
