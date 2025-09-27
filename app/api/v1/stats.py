from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy import func
from sqlmodel import select
from starlette.status import (
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from app.core.dependencies import (
    RateLimiter,
    SessionDep,
)
from app.models.image import Image, ImageReviewStatus
from app.models.label_category import (
    LabelSuperCategory,
    LabelSuperCategoryPublic,
)
from app.models.models import (
    StatsOut,
)
from app.models.team import Team
from app.services.monitoring import get_uptime

router = APIRouter()


@router.get("/ping", tags=["Stats"])
async def ping() -> dict[str, str]:
    return {"ping": "pong!"}


@router.get(
    "/stats",
    tags=["Stats"],
    dependencies=[Depends(RateLimiter(requests_limit=20, time_window=10))],
)
def get_stats(session: SessionDep) -> StatsOut:
    """
    Get stats about the entire database
    """
    out = StatsOut(
        image_count=session.exec(
            select(func.count())
            .select_from(Image)
            .where(Image.review_status == ImageReviewStatus.APPROVED)
        ).one(),
        un_reviewed_image_count=session.exec(
            select(func.count())
            .select_from(Image)
            .where(Image.review_status != ImageReviewStatus.APPROVED)
        ).one(),
        team_count=session.exec(select(func.count()).select_from(Team)).one(),
        uptime=get_uptime(),
    )
    return out


@router.get("/stats/labels", tags=["Stats"])
def get_label_info(
    session: SessionDep,
) -> list[LabelSuperCategoryPublic]:
    categories = session.exec(select(LabelSuperCategory)).all()

    if not categories:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="No categories found"
        )

    output = []
    for catagory in categories:
        public = catagory.get_public()
        output.append(public)

    return output
