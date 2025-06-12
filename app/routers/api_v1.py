from fastapi import APIRouter, Depends

from ..dependencies import api_key_scheme

router = APIRouter()

# ========== { Public API } ==========

@router.get("/stats", tags=["Public", "Stats"])
def get_stats():
    """
    Get stats about the entire database
    """
    pass

@router.get("/stats/team/{team_number}", tags=["Public", "Stats"])
def get_team_stats(team_number: int):
    """
    Get stats about individual teams

    - **team**: The team to look at
    """
    pass

# ========== { Private API } ==========

@router.get("/status/{batch_id}", tags=["Auth Required",  "Stats"])
def get_batch_status(batch_id: int, api_key: str = Depends(api_key_scheme)):
    pass

@router.post("/upload", tags=["Auth Required"])
def upload(api_key: str = Depends(api_key_scheme)):
    pass

@router.get("/download", tags=["Auth Required"])
def download_batch(api_key: str = Depends(api_key_scheme)):
    pass

@router.get("/download/{image_id}", tags=["Auth Required"])
def download_image(image_id: int, api_key: str = Depends(api_key_scheme)):
    pass
