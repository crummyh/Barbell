from uuid import UUID

from sqlmodel import Session

from app.core.helpers import validated
from app.models.upload_batch import UploadBatch, UploadBatchCreate, UploadBatchUpdate


def create(session: Session, upload_batch_create: UploadBatchCreate) -> UploadBatch:
    upload_batch = validated(UploadBatch, upload_batch_create)
    session.add(upload_batch)
    session.commit()
    session.refresh(upload_batch)
    return upload_batch


def get(session: Session, id: UUID) -> UploadBatch | None:
    upload_batch: UploadBatch | None = session.get(UploadBatch, id)
    return upload_batch


def update(
    session: Session, id: UUID, upload_batch_update: UploadBatchUpdate | dict
) -> UploadBatch | None:
    upload_batch: UploadBatch | None = session.get(UploadBatch, id)
    if upload_batch is None:
        return None

    if isinstance(upload_batch_update, dict):
        upload_batch_update = UploadBatchUpdate(**upload_batch_update)

    new_upload_batch_data = upload_batch_update.model_dump(exclude_unset=True)
    upload_batch.sqlmodel_update(new_upload_batch_data)
    session.add(upload_batch)
    session.commit()
    session.refresh(upload_batch)
    return upload_batch


def delete(session: Session, id: UUID) -> bool:
    upload_batch = session.get(UploadBatch, id)
    if upload_batch is None:
        return False

    session.delete(upload_batch)
    session.commit()
    return True
