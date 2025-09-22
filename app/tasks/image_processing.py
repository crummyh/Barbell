import tarfile
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import IO, BinaryIO
from uuid import UUID

from PIL import Image as PIL_Image
from sqlmodel import Session

from app.core import config
from app.crud import image as image_crud
from app.crud import upload_batch
from app.database import engine
from app.models.image import ImageCreate
from app.models.upload_batch import UploadBatch, UploadStatus
from app.services.buckets import create_image, get_upload_batch


async def process_batch_async(batch_id: UUID) -> None:
    with Session(engine) as session:
        batch = upload_batch.get(session, batch_id)  # Get the batch
        if not batch:
            raise ValueError(f"UploadBatch with id {batch_id} not found")

        # Update the status and time to show that we have started
        upload_batch.update(
            session,
            batch_id,
            {
                "status": UploadStatus.PROCESSING,
                "start_time": datetime.now(timezone.utc),
            },
        )

        try:
            file = get_upload_batch(batch_id)  # Get the actual file
            with tarfile.open(fileobj=file, mode="r:gz") as tar:
                image_files = [  # Get all the valid images in the archive
                    m for m in tar.getmembers() if m.isfile()
                ]
                # Update the # of total images
                upload_batch.update(
                    session, batch_id, {"images_total": len(image_files)}
                )

                # Loop through every image
                for member in image_files:
                    try:
                        if not validate_image_pre(member):
                            upload_batch.update(
                                session,
                                batch_id,
                                {"images_rejected": batch.images_rejected + 1},
                            )
                            continue  # Stop the loop here and start the next image

                        image = tar.extractfile(member)  # Extract the image
                        assert image  # The image has to exist

                        # Validate the image and add it to the database
                        if validate_image(image):
                            image_entry = image_crud.create(
                                session, ImageCreate(batch=batch_id), batch.user
                            )

                            image = _force_image_format(image)

                            assert (
                                image_entry.id
                            )  # The ID is generated, so we assume it exists
                            create_image(image, image_entry.id)  # Add the image to S3

                            # Increment the valid image count
                            upload_batch.update(
                                session,
                                batch_id,
                                {"images_valid": batch.images_valid + 1},
                            )

                        else:
                            # The image is not valid
                            upload_batch.update(
                                session,
                                batch_id,
                                {"images_rejected": batch.images_rejected + 1},
                            )

                    except Exception:
                        # Something went wrong somewhere, and the image is passed
                        upload_batch.update(
                            session,
                            batch_id,
                            {"images_rejected": batch.images_rejected + 1},
                        )
                        raise

            if batch.images_valid == 0:
                # If we made it through all images, but they
                # all failed, the batch is a failure.
                upload_batch.update(session, batch_id, {"status": UploadStatus.FAILED})
            else:
                # but if at least some worked then we are done!
                upload_batch.update(
                    session, batch_id, {"status": UploadStatus.COMPLETED}
                )

        except Exception as e:
            # Something went wrong, so we rollback and say we failed
            session.rollback()
            upload_batch.update(
                session,
                batch_id,
                {"status": UploadStatus.FAILED, "error_message": str(e)},
            )
            raise
        else:
            session.commit()


def _force_image_format(image: BinaryIO | IO[bytes]) -> BytesIO:
    with PIL_Image.open(image) as img:
        output = BytesIO()
        img.save(output, format=config.IMAGE_STORAGE_FORMAT)
        output.seek(0)
        return output


def validate_image(image_path: BinaryIO | IO[bytes]) -> bool:
    """Validate image meets requirements (640x640, etc.)"""
    try:
        with PIL_Image.open(image_path) as img:
            return bool(img.size == (640, 640))
    except Exception:
        return False


def validate_image_pre(image_member: tarfile.TarInfo) -> bool:
    """Validate image *before* extracting"""
    return Path(image_member.name).suffix.lower() in config.ALLOWED_IMAGE_EXTENSIONS


def estimate_upload_processing_time(session: Session, batch_id: UUID) -> float:
    """Estimate the time left in processing (in seconds)"""
    batch = session.get(UploadBatch, batch_id)
    if not batch:
        raise IndexError("batch id not found")

    if batch.status in {UploadStatus.COMPLETED, UploadStatus.FAILED}:
        return 0

    if batch.status == UploadStatus.UPLOADING:
        return config.DEFAULT_PROCESSING_TIME

    images_done = batch.images_valid + batch.images_rejected
    progress = images_done / batch.images_total
    assert batch.start_time
    delta_time = (batch.start_time - datetime.now(timezone.utc)).total_seconds()

    return float(delta_time / progress)
