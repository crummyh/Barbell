from sqlmodel import Session

from app.models.annotation import Annotation, AnnotationCreate, AnnotationUpdate


def create(session: Session, annotation_create: AnnotationCreate) -> Annotation:
    annotation: Annotation = Annotation.model_validate(annotation_create)
    session.add(annotation)
    session.commit()
    session.refresh(annotation)
    return annotation


def get(session: Session, id: int) -> Annotation | None:
    annotation = session.get(Annotation, id)
    assert isinstance(annotation, Annotation) or annotation is None
    return annotation


def update(
    session: Session, id: int, annotation_update: AnnotationUpdate | dict
) -> Annotation | None:
    annotation: Annotation | None = session.get(Annotation, id)
    if annotation is None:
        return None

    if isinstance(annotation_update, dict):
        annotation_update = AnnotationUpdate(**annotation_update)

    new_annotation_data = annotation_update.model_dump(exclude_unset=True)
    annotation.sqlmodel_update(new_annotation_data)
    session.add(annotation)
    session.commit()
    session.refresh(annotation)
    return annotation


def delete(session: Session, id: int) -> bool:
    annotation = session.get(Annotation, id)
    if annotation is None:
        return False

    session.delete(annotation)
    session.commit()
    return True
