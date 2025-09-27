from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
)

from app.core.dependencies import (
    minimum_role,
    rate_limit_config,
)
from app.models.models import (
    RateLimitUpdate,
)
from app.models.user import User, UserRole

router = APIRouter()


@router.post("/admin/rate-limit/update")
def update_rate_limit(
    cfg: RateLimitUpdate, user: Annotated[User, Depends(minimum_role(UserRole.ADMIN))]
) -> dict:
    rate_limit_config[cfg.route]["requests_limit"] = cfg.requests_limit
    rate_limit_config[cfg.route]["time_window"] = cfg.time_window
    return {"message": "Rate limit updated", "config": rate_limit_config}


@router.get("/admin/rate-limit")
def get_rate_limit(
    user: Annotated[User, Depends(minimum_role(UserRole.ADMIN))],
) -> dict:
    return rate_limit_config
