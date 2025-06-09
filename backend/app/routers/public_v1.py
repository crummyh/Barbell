from fastapi import APIRouter

router = APIRouter()

@router.get("/status/{batch_id}")
def get_batch_status(batch_id: int):
    pass

@router.get("/stats")
def get_stats():
    pass

@router.get("stats/team/{team}")
def get_team_stats(team: int):
    pass
