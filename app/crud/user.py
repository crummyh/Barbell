from sqlmodel import Session, select

from app.core.dependencies import get_password_hash
from app.models.models import User, UserCreate, UserUpdate


def create_user(session: Session, user_create: UserCreate) -> User:
    user_create.password = get_password_hash(user_create.password)

    user = User.model_validate(user_create)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def get_user(session: Session, id: int) -> User | None:
    user = session.get(User, id)
    return user

def get_user_from_username(session: Session, username: str) -> User | None:
    user = session.exec(select(User).where(User.username == username)).one()
    return user

def update_user(session: Session, id: int, user_update: UserUpdate) -> User | None:
    if user_update.password is not None:
        user_update.password = get_password_hash(user_update.password)

    user = session.get(User, id)
    if user is None:
        return None

    new_user_data = user_update.model_dump(exclude_unset=True)
    user.sqlmodel_update(new_user_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def delete_user(session: Session, id: int) -> bool:
    user = session.get(User, id)
    if user is None:
        return False

    session.delete(user)
    session.commit()
    return True
