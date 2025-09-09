from sqlmodel import Session
from app.models.models import UserCreate, UserUpdate, UserPublic, User

def create_user(session: Session, user_create: UserCreate) -> User:
    user = User.model_validate(user_create)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def get_user(session: Session, id: int) -> User | None:
    user = session.get(User, id)
    return user

def get_public_user(session: Session, id: int) -> UserPublic | None:
    user = get_user(session, id)
    if user is None:
        return None
    return public_user.get_public()

def update_user(session: Session, id: int, user_update: UserUpdate) -> User:
    user = session.get(User, id)
    new_user_data = user_update.model_dump(exclude_unset=True)
    user.sqlmodel_update(new_user_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def delete_user(session: Session, id: int) -> None:
    user = session.get(user, id)
    session.delete(user)
    session.commit()