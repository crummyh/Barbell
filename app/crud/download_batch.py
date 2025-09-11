from uuid import UUID

from sqlmodel import Session

from app.models.models import DownloadBatch, DownloadBatchCreate, DownloadBatchUpdate


def create(session: Session, download_batch_create: DownloadBatchCreate) -> DownloadBatch:
    download_batch = DownloadBatch.model_validate(download_batch_create)
    session.add(download_batch)
    session.commit()
    session.refresh(download_batch)
    return download_batch

def get(session: Session, id: UUID) -> DownloadBatch | None:
    download_batch = session.get(DownloadBatch, id)
    return download_batch

def update(session: Session, id: UUID, download_batch_update: DownloadBatchUpdate) -> DownloadBatch | None:
    download_batch = session.get(DownloadBatch, id)
    if download_batch is None:
        return None

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
