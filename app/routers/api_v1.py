from fastapi import APIRouter

router = APIRouter()

# ========== { Public API } ==========

@router.get("/stats")
def get_stats():
    pass

@router.get("stats/team/{team}")
def get_team_stats(team: int):
    pass

# ========== { Private API } ==========

@router.get("/status/{batch_id}")
# @limiter.limit("10/second")
def get_batch_status(batch_id: int):
    pass

@router.post("/upload")
# @limiter.limit("5/minutes")
def upload():
    pass

@router.get("/download")
def download_batch():
    pass

@router.get("/download/{image_id}")
def download_image(image_id: int):
    pass
