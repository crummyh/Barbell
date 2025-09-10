from sqlmodel import Session

from app.models.models import Annotation, AnnotationCreate, AnnotationUpdate


def create_annotation(session: Session, annotation_create: AnnotationCreate) -> Annotation:
    annotation = Annotation.model_validate(annotation_create)
    session.add(annotation)
    session.commit()
    session.refresh(annotation)
    return annotation

def get_annotation(session: Session, id: int) -> Annotation | None:
    annotation = session.get(Annotation, id)
    return annotation

def update_annotation(session: Session, id: int, annotation_update: AnnotationUpdate) -> Annotation | None:
    annotation = session.get(Annotation, id)
    if annotation is None:
        return None

    new_annotation_data = annotation_update.model_dump(exclude_unset=True)
    annotation.sqlmodel_update(new_annotation_data)
    session.add(annotation)
    session.commit()
    session.refresh(annotation)
    return annotation

def delete_annotation(session: Session, id: int) -> bool:
    annotation = session.get(Annotation, id)
    if annotation is None:
        return False

    session.delete(annotation)
    session.commit()
    return True
