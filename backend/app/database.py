from collections.abc import Generator
from typing import Any

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import DATABASE_URL

connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL)


def get_session() -> Generator[Session, Any, None]:
    with Session(engine) as session:
        yield session


def init_db() -> None:
    from app.models import configure_relationships
    from app.models.annotation import Annotation  # noqa: F401
    from app.models.download_batch import DownloadBatch  # noqa: F401
    from app.models.image import Image  # noqa: F401
    from app.models.team import Team  # noqa: F401
    from app.models.upload_batch import UploadBatch  # noqa: F401
    from app.models.user import User  # noqa: F401

    configure_relationships()

    Annotation.model_rebuild()
    DownloadBatch.model_rebuild()
    Image.model_rebuild()
    Team.model_rebuild()
    UploadBatch.model_rebuild()
    User.model_rebuild()

    SQLModel.metadata.create_all(engine)
