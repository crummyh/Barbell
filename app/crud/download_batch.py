from uuid import UUID

from sqlmodel import Session

from app.models.download_batch import (
    DownloadBatch,
    DownloadBatchCreate,
    DownloadBatchUpdate,
)
from app.models.user import User


def create(
    session: Session, download_batch_create: DownloadBatchCreate, user: User
) -> DownloadBatch:
    download_batch = DownloadBatch.model_validate(download_batch_create)
    assert user.id
    download_batch.user_id = user.id
    session.add(download_batch)
    session.commit()
    session.refresh(download_batch)
    return download_batch


def get(session: Session, id: UUID) -> DownloadBatch | None:
    download_batch = session.get(DownloadBatch, id)
    return download_batch


def update(
    session: Session, id: UUID, download_batch_update: DownloadBatchUpdate | dict
) -> DownloadBatch | None:
    download_batch = session.get(DownloadBatch, id)
    if download_batch is None:
        return None

    if isinstance(download_batch_update, dict):
        download_batch_update = DownloadBatchUpdate(**download_batch_update)

    new_download_batch_data = download_batch_update.model_dump(exclude_unset=True)
    download_batch.sqlmodel_update(new_download_batch_data)
    session.add(download_batch)
    session.commit()
    session.refresh(download_batch)
    return download_batch


def delete(session: Session, id: UUID) -> bool:
    download_batch = session.get(DownloadBatch, id)
    if download_batch is None:
        return False

    session.delete(download_batch)
    session.commit()
    return True
