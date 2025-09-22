from uuid import UUID

from sqlmodel import Session

from app.models.image import Image, ImageCreate, ImageUpdate
from app.models.user import User


def create(session: Session, image_create: ImageCreate, user: User) -> Image:
    image: Image = Image.model_validate(image_create)
    assert user.id
    image.created_by = user.id
    session.add(image)
    session.commit()
    session.refresh(image)
    return image


def get(session: Session, id: UUID) -> Image | None:
    image: Image | None = session.get(Image, id)
    return image


def update(
    session: Session, id: UUID, image_update: ImageUpdate | dict
) -> Image | None:
    image: Image | None = session.get(Image, id)
    if image is None:
        return None

    if isinstance(image_update, dict):
        image_update = ImageUpdate(**image_update)

    new_image_data = image_update.model_dump(exclude_unset=True)
    image.sqlmodel_update(new_image_data)
    session.add(image)
    session.commit()
    session.refresh(image)
    return image


def delete(session: Session, id: UUID) -> bool:
    # TODO: Delete in S3 as well

    image = session.get(Image, id)
    if image is None:
        return False

    session.delete(image)
    session.commit()
    return True
