import tarfile

from fastapi import APIRouter, Depends, UploadFile
from fastapi.exceptions import HTTPException
from sqlalchemy import func
from sqlmodel import Session, select

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

    - **team**: The team to look at
    """
    out = TeamStatsOut(
        image_count=0,
        years_available=[2025],
        upload_batches=2
    )
    return out

# ========== { Auth API } ==========

@router.get("/status/{batch_id}", tags=["Auth Required",  "Stats"])
def get_batch_status(
    batch_id: int,
    api_key: str = Depends(api_key_scheme),
    session: Session = Depends(get_session)
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
    archive: UploadFile,
    api_key: str = Depends(api_key_scheme),
    session: Session = Depends(get_session)
):
    team_id = check_api_key(api_key, session)

    if not tarfile.is_tarfile(archive.file):
        raise HTTPException(status_code=415, detail="File must be of type .tar.gz")

    if archive.size and (archive.size > config.MAX_FILE_SIZE):
        raise HTTPException(status_code=413, detail=f"File too large. Max size: {config.MAX_FILE_SIZE / (1024**3):.1f}GB")

    try:
        batch = UploadBatch(
            team_id=team_id,
            status=UploadStatus.UPLOADING,
            file_size=archive.size
        )
        session.add(batch)
    except:
        session.rollback()
        raise
    else:
        session.commit()

    pass

@router.get("/download", tags=["Auth Required"])
def download_batch(
    api_key: str = Depends(api_key_scheme),
    session: Session = Depends(get_session)
):
    team_id = check_api_key(api_key, session)
    pass



@router.get("/download/{image_id}", tags=["Auth Required"])
def download_image(
    image_id: int,
    api_key: str = Depends(api_key_scheme),
    session: Session = Depends(get_session)
):
    team_id = check_api_key(api_key, session)
    if not team_id:
        raise HTTPException(status_code=403, detail="API Key is incorrect")
    pass

# ========== { Internal API } ==========
