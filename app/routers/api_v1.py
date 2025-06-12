from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlmodel import Session, select

from ..database import get_session
from ..dependencies import api_key_scheme
from ..models import Image, StatsOut, StatusOut, Team, TeamStatsOut

router = APIRouter()

# ========== { Public API } ==========

@router.get("/stats", tags=["Public", "Stats"])
def get_stats(session: Session = Depends(get_session)):
    """
    Get stats about the entire database
    """
    out = StatsOut(
        image_count=session.exec(select(func.count()).select_from(Image)).one(),
        team_count=session.exec(select(func.count()).select_from(Team)).one()
    )
    return out

@router.get("/stats/team/{team_number}", tags=["Public", "Stats"])
def get_team_stats(team_number: int, session: Session = Depends(get_session)):
    """
    Get stats about individual teams

    - **team**: The team to look at
    """
    out = TeamStatsOut
    return out

# ========== { Auth API } ==========

@router.get("/status/{batch_id}", tags=["Auth Required",  "Stats"])
def get_batch_status(
    batch_id: int,
    api_key: str = Depends(api_key_scheme),
    session: Session = Depends(get_session)
):
    out = StatusOut
    return out

@router.post("/upload", tags=["Auth Required"])
def upload(
    api_key: str = Depends(api_key_scheme),
    session: Session = Depends(get_session)
):
    pass

@router.get("/download", tags=["Auth Required"])
def download_batch(
    api_key: str = Depends(api_key_scheme),
    session: Session = Depends(get_session)
):
    pass

@router.get("/download/{image_id}", tags=["Auth Required"])
def download_image(
    image_id: int,
    api_key: str = Depends(api_key_scheme),
    session: Session = Depends(get_session)
):
    pass

# ========== { Internal API } ==========
