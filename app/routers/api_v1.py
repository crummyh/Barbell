from hashlib import md5
import tarfile
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile
from fastapi.exceptions import HTTPException
from sqlalchemy import func
from sqlmodel import Session, select

from app.buckets import create_upload_batch
from app.helpers import get_hash_with_streaming, get_id_from_team_number

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

    images = session.exec(select(Image).where(Image.capture_time == team)).all()
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
    batch_id: int,
    api_key:  str     = Depends(api_key_scheme),
    session:  Session = Depends(get_session)
) -> StatusOut:
    team_id = check_api_key(api_key, session)

    out = StatusOut(
        batch_id=0,
        team=4786,
        status=UploadStatus.UPLOADING,
        file_size=1,
        images_valid=0,
        images_rejected=0,
        images_total=0,
        file_path=None,
        error_msg=None
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
):
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
    except:  # noqa: E722
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail="There was an error adding the batch to the database. Sorry!"
        )
    else:
        session.commit()

        try:
            create_upload_batch(archive.file, )

    pass

@router.get("/download", tags=["Auth Required"])
def download_batch(
    api_key: str     = Depends(api_key_scheme),
    session: Session = Depends(get_session)
):
    team_id = check_api_key(api_key, session)
    pass

@router.get("/download/{image_id}", tags=["Auth Required"])
def download_image(
    image_id: int,
    api_key: str     = Depends(api_key_scheme),
    session: Session = Depends(get_session)
):
    team_id = check_api_key(api_key, session)
    if not team_id:
        raise HTTPException(status_code=403, detail="API Key is incorrect")
    pass
