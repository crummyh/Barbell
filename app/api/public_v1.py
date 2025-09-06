import tarfile
from datetime import datetime, timezone
from typing import Annotated, Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, UploadFile
from fastapi.exceptions import HTTPException
from sqlalchemy import func
from sqlmodel import Session, select
from starlette.responses import StreamingResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.core import config
from app.core.dependencies import (
    RateLimiter,
    generate_api_key,
    get_password_hash,
    handle_api_key,
)
from app.core.helpers import (
    get_hash_with_streaming,
    get_username_from_id,
)
from app.db.database import get_session
from app.models.models import (
    DownloadRequest,
    DownloadStatus,
    DownloadStatusOut,
    ImageReviewStatus,
    StatsOut,
    UploadStatus,
    UploadStatusOut,
)
from app.models.schemas import (
    DownloadBatch,
    Image,
    LabelSuperCategory,
    Team,
    UploadBatch,
    User,
)
from app.services.buckets import create_upload_batch, get_download_batch
from app.services.monitoring import get_uptime
from app.tasks.download_packaging import create_download_batch
from app.tasks.image_processing import (
    estimate_upload_processing_time,
    process_batch_async,
    validate_image_pre,
)

router = APIRouter()

# ========== { Public API } ========== #

@router.get("/stats", tags=["Public", "Stats"], dependencies=[Depends(RateLimiter(requests_limit=20, time_window=10))])
def get_stats(session: Annotated[Session, Depends(get_session)]) -> StatsOut:
    """
    Get stats about the entire database
    """
    out = StatsOut(
        image_count=session.exec(select(func.count()).select_from(Image).where(Image.review_status == ImageReviewStatus.APPROVED)).one(),
        un_reviewed_image_count=session.exec(select(func.count()).select_from(Image).where(Image.review_status != ImageReviewStatus.APPROVED)).one(),
        team_count=session.exec(select(func.count()).select_from(Team)).one(),
        uptime=get_uptime()
    )
    return out

@router.get("/stats/labels")
def get_label_info(
    session: Annotated[Session, Depends(get_session)]
) -> List[Dict[str, Any]]:
    categories = session.exec(select(LabelSuperCategory)).all()

    if not categories:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No categories found"
        )

    output = []
    for catagory in categories:
        output.append({
            "id": catagory.id,
            "name": catagory.name,
            "categories": catagory.sub_categories
        })

    return output

# ========== { Auth API } ========== #

@router.get("/upload/status/{batch_id}", tags=["Auth Required",  "Stats"], dependencies=[Depends(RateLimiter(requests_limit=30, time_window=10))])
def get_upload_batch_status(
    batch_id: UUID,
    user: Annotated[User, Depends(handle_api_key)],
    session: Annotated[Session, Depends(get_session)]
) -> UploadStatusOut:

    batch = session.get(UploadBatch, batch_id)
    if not batch:
        raise HTTPException(
            status_code=404,
            detail="Batch not found"
        )

    out = UploadStatusOut(
        batch_id=batch_id,
        user=get_username_from_id(batch.user, session),
        status=batch.status,
        file_size=batch.file_size,
        images_valid=batch.images_valid,
        images_rejected=batch.images_rejected,
        images_total=batch.images_total,
        estimated_time_left=estimate_upload_processing_time(session,batch_id),
        error_msg=batch.error_message
    )
    return out

@router.post("/upload/test")
async def test_upload_archive(
    archive:          UploadFile,
    hash:             str,
    user: Annotated[User, Depends(handle_api_key)]
):
    if not tarfile.is_tarfile(archive.file):
        raise HTTPException(
            status_code=415,
            detail="File must be of type .tar.gz"
        )

    if archive.size and (archive.size > config.MAX_FILE_SIZE):
        raise HTTPException(
            status_code=413,
            detail=f"File is too large. Max size: {config.MAX_FILE_SIZE / (1024**3):.1f}GB"
        )

    if get_hash_with_streaming(archive.file, config.BUCKET_NAME_HASH_ALGORITHM) != hash:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is corrupted (hash mismatch) (Are you using sha256?)"
        )

    with tarfile.open(fileobj=archive.file, mode="r:gz") as tar:
        image_files = [
            m for m in tar.getmembers()
            if m.isfile()
        ]

        if len(image_files) == 0:
            raise HTTPException(
                status_code=400,
                detail="Archive is empty. Are the images in root?"
            )

        for i in image_files:
            if not validate_image_pre(i):
                raise HTTPException(
                    status_code=400,
                    detail=f"Image \"{i.name}\" is not a supported file type. See `PIL.Image.registered_extensions().items()`"
                )

    return "Success"

@router.post("/upload", tags=["Auth Required"], dependencies=[Depends(RateLimiter(requests_limit=2, time_window=60))])
async def upload(
    archive:          UploadFile,
    hash:             str,
    background_tasks: BackgroundTasks,
    user: Annotated[User, Depends(handle_api_key)],
    session: Annotated[Session, Depends(get_session)],
    capture_time:     datetime = datetime.now(timezone.utc)
) -> UploadStatusOut:
    """
    Upload images to the dataset. Requires and API key

    `archive`: The images in a .tar.gz archive

    `hash`: A ***sha256*** hash of the archive

    `capture_time`: The rough time that the data was gathered
    """

    await test_upload_archive(archive, hash, user)

    try:
        assert user.id
        batch = UploadBatch(
            user=user.id,
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


    async def upload_archive():
        assert batch.id
        create_upload_batch(archive.file, batch.id)
        background_tasks.add_task(process_batch_async, batch_id=batch.id)

    background_tasks.add_task(upload_archive)

    assert batch.id
    return UploadStatusOut(
        batch_id=batch.id,
        user=get_username_from_id(batch.user, session),
        status=UploadStatus.PROCESSING,
        file_size=archive.size,
        images_valid=None,
        images_total=None,
        images_rejected=None,
        estimated_time_left=config.DEFAULT_PROCESSING_TIME,
        error_msg=None
    )

@router.get("/download/status/{batch_id}", tags=["Auth Required",  "Stats"], dependencies=[Depends(RateLimiter(requests_limit=30, time_window=10))])
def get_download_batch_status(
    batch_id: UUID,
    user: Annotated[User, Depends(handle_api_key)],
    session: Annotated[Session, Depends(get_session)]
) -> DownloadStatusOut:

    batch = session.get(DownloadBatch, batch_id)
    if not batch:
        raise HTTPException(
            status_code=404,
            detail="Batch not found"
        )

    out = DownloadStatusOut(
        id=batch_id,
        user=get_username_from_id(batch.user, session),
        status=batch.status,
        non_match_images=batch.non_match_images,
        image_count=batch.image_count,
        annotations=batch.annotations,
        start_time=batch.start_time,
        hash=batch.hash,
        error_message=batch.error_message
    )
    return out

@router.put("/download/request", tags=["Auth Required"], dependencies=[Depends(RateLimiter(requests_limit=2, time_window=60))])
def request_download_batch(
    request: DownloadRequest,
    background_tasks: BackgroundTasks,
    user: Annotated[User, Depends(handle_api_key)],
    session: Annotated[Session, Depends(get_session)]
):
    try:
        assert user.id
        batch = DownloadBatch(
            user=user.id,
            status=DownloadStatus.STARTING,
            non_match_images=request.non_match_images,
            image_count=request.count,
            annotations=request.annotations
        )
        session.add(batch)
        session.commit()
        session.refresh(batch)
        assert batch.id

    except Exception:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add batch to database"
        )

    else:
        background_tasks.add_task(create_download_batch, batch_id=batch.id)
        return DownloadStatusOut(
            id=batch.id,
            user=get_username_from_id(batch.user, session),
            status=batch.status,
            non_match_images=batch.non_match_images,
            image_count=batch.image_count,
            annotations=batch.annotations,
            start_time=batch.start_time,
            hash=batch.hash,
            error_message=batch.error_message
        )

@router.put("/download/get/{batch_id}", tags=["Auth Required"], dependencies=[Depends(RateLimiter(requests_limit=2, time_window=60))])
def download_batch(
    batch_id: UUID,
    user: Annotated[User, Depends(handle_api_key)],
    session: Annotated[Session, Depends(get_session)]
):
    try:
        batch = session.get(DownloadBatch, batch_id)
        assert batch
    except Exception:
        raise HTTPException(
            status_code=404,
            detail="Batch not found"
        )

    if batch.status != DownloadStatus.READY:
        raise HTTPException(
            status_code=400,
            detail="Batch is not ready to download"
        )

    return StreamingResponse(
        content=get_download_batch(batch_id),
        media_type="application/gzip",
        headers={"Content-Disposition": "attachment; filename=images.tar.gz"}
    )


# ==========={ Management }=========== #

@router.put("/rotate-key", dependencies=[Depends(RateLimiter(requests_limit=1, time_window=60))])
def rotate_api_key(
    batch_id: UUID,
    user: Annotated[User, Depends(handle_api_key)],
    session: Annotated[Session, Depends(get_session)]
):
    try:
        user.api_key = get_password_hash(generate_api_key())
        session.add(user)
    except Exception:
        session.rollback()
    else:
        session.commit()

    session.refresh(user)
    return user.api_key
