from uuid import UUID

from sqlmodel import Session

from app.models.models import Image, ImageCreate, ImageUpdate


def create(session: Session, image_create: ImageCreate) -> Image:
    image = Image.model_validate(image_create)
    session.add(image)
    session.commit()
    session.refresh(image)
    return image

def get(session: Session, id: UUID) -> Image | None:
    image = session.get(Image, id)
    return image

def update(session: Session, id: UUID, image_update: ImageUpdate | dict) -> Image | None:
    image = session.get(Image, id)
    if image is None:
        return None

    if isinstance(image_update, dict):
        image_update = AnnotationCreate(**image_update)

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
