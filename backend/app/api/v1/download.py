from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
)
from fastapi.params import Security
from fastapi.responses import StreamingResponse
from starlette.status import (
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from app.core.dependencies import (
    RateLimiter,
    SessionDep,
    get_current_user,
)
from app.crud import download_batch
from app.models.download_batch import (
    DownloadBatchCreate,
    DownloadBatchPublic,
    DownloadStatus,
)
from app.models.user import User
from app.services.buckets import get_download_batch
from app.tasks.download_packaging import create_download_batch

router = APIRouter()


@router.get(
    "/status/{batch_id}",
    tags=["Download"],
    dependencies=[Depends(RateLimiter(requests_limit=30, time_window=10))],
)
def get_download_batch_status(
    batch_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
) -> DownloadBatchPublic:
    batch = download_batch.get(session, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    out = batch.get_public()
    return out


@router.put(
    "/request",
    tags=["Download"],
    dependencies=[Depends(RateLimiter(requests_limit=2, time_window=60))],
)
def request_download_batch(
    request: DownloadBatchCreate,
    background_tasks: BackgroundTasks,
    user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
) -> DownloadBatchPublic:
    try:
        batch = download_batch.create(session, request, user)

    except Exception:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add batch to database",
        ) from None

    background_tasks.add_task(create_download_batch, batch_id=batch.id)
    return batch.get_public()


@router.put(
    "/get/{batch_id}",
    tags=["Download"],
    dependencies=[Depends(RateLimiter(requests_limit=2, time_window=60))],
)
def download_download_batch(
    batch_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
) -> StreamingResponse:
    batch = download_batch.get(session, batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")

    if batch.status != DownloadStatus.READY:
        raise HTTPException(status_code=400, detail="Batch is not ready to download")

    return StreamingResponse(
        content=get_download_batch(batch_id),
        media_type="application/gzip",
        headers={"Content-Disposition": "attachment; filename=images.tar.gz"},
    )


@router.get("/history")
def get_download_batch_history(
    session: SessionDep,
    current_user: Annotated[User, Security(get_current_user)],
) -> list[DownloadBatchPublic] | None:
    batches = current_user.download_batches
    if len(batches) == 0:
        return None

    return [i.get_public() for i in batches]
