import tarfile
from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Security,
    UploadFile,
)

from app.core import config
from app.core.dependencies import (
    RateLimiter,
    SessionDep,
    get_current_user,
)
from app.core.helpers import (
    get_hash_with_streaming,
)
from app.crud import upload_batch
from app.models.upload_batch import (
    UploadBatchCreate,
    UploadBatchPublic,
)
from app.models.user import User
from app.services.buckets import create_upload_batch
from app.tasks.image_processing import (
    estimate_upload_processing_time,
    process_batch_async,
    validate_image_pre,
)

router = APIRouter()


@router.get(
    "/status/{batch_id}",
    tags=["Upload"],
    dependencies=[Depends(RateLimiter(requests_limit=30, time_window=10))],
)
def get_upload_batch_status(
    batch_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
) -> UploadBatchPublic:
    batch = upload_batch.get(session, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    out = batch.get_public()
    out.estimated_time_left = estimate_upload_processing_time(session, batch_id)

    return out


@router.post("/test", tags=["Upload"])
async def check_upload_archive(
    archive: UploadFile, hash: str, user: Annotated[User, Depends(get_current_user)]
) -> dict[str, str]:
    if not tarfile.is_tarfile(archive.file):
        raise HTTPException(status_code=415, detail="File must be of type .tar.gz")

    if archive.size and (archive.size > config.MAX_FILE_SIZE):
        raise HTTPException(
            status_code=413,
            detail=f"File is too large. Max size: {config.MAX_FILE_SIZE / (1024**3):.1f}GB",
        )

    if get_hash_with_streaming(archive.file, config.BUCKET_NAME_HASH_ALGORITHM) != hash:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is corrupted (hash mismatch) (Are you using sha256?)",
        )

    archive.file.seek(0)
    with tarfile.open(fileobj=archive.file, mode="r:gz") as tar:
        image_files = [m for m in tar.getmembers() if m.isfile()]

        if len(image_files) == 0:
            raise HTTPException(
                status_code=400, detail="Archive is empty. Are the images in root?"
            )

        for i in image_files:
            if not validate_image_pre(i):
                raise HTTPException(
                    status_code=400,
                    detail=f'Image "{i.name}" is not a supported file type. See `PIL.Image.registered_extensions().items()`',
                )

    return {"status": "success"}


@router.post(
    "",
    tags=["Upload"],
    dependencies=[Depends(RateLimiter(requests_limit=2, time_window=60))],
)
async def upload(
    archive: UploadFile,
    hash: str,
    background_tasks: BackgroundTasks,
    user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
    capture_time: datetime = datetime.now(timezone.utc),
) -> UploadBatchPublic:
    """
    Upload images to the dataset. Requires an API key

    `archive`: The images in a .tar.gz archive

    `hash`: A ***sha256*** hash of the archive

    `capture_time`: The rough time that the data was gathered
    """

    await check_upload_archive(archive, hash, user)

    try:
        assert user.id
        assert archive.size

        batch = upload_batch.create(
            session,
            UploadBatchCreate(
                capture_time=capture_time,
                file_size=archive.size,
                user_id=user.id,
            ),
        )
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail="There was an error adding the batch to the database. Sorry!",
        ) from None

    assert batch.id
    create_upload_batch(archive.file, batch.id)

    background_tasks.add_task(process_batch_async, batch_id=batch.id)

    out = batch.get_public()
    out.estimated_time_left = config.DEFAULT_PROCESSING_TIME
    return out


@router.get("/history")
def get_upload_batch_history(
    session: SessionDep,
    current_user: Annotated[User, Security(get_current_user)],
) -> list[UploadBatchPublic] | None:
    batches = current_user.upload_batches
    if len(batches) == 0:
        return None

    return [i.get_public() for i in batches]
