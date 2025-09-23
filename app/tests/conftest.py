from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select

from app.core.config import DATABASE_URL
from app.core.dependencies import get_password_hash
from app.database import get_session
from app.main import app
from app.models.user import User, UserCreate

# Engine just for tests
engine = create_engine(DATABASE_URL, echo=True)


@pytest.fixture(scope="session", autouse=True)
def prepare_database() -> Generator[None, None, None]:
    """Create all tables at the start of the test session, drop them at the end."""
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """Provide a fresh DB session for each test."""
    with Session(engine) as session:
        yield session
        session.rollback()  # rollback after each test just in case


@pytest.fixture(scope="function")
def client(test_db: Session) -> Generator[TestClient, None, None]:
    """
    Override FastAPI's get_session dependency to use the test session.
    """

    def override_get_db() -> Generator[Session, None, None]:
        yield test_db

    app.dependency_overrides[get_session] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


TEST_USER_API_KEY = "c8d5dbce53db68f911fdb00272de9067"


@pytest.fixture(scope="function")
def user(test_db: Session) -> Generator[User, None, None]:
    user = test_db.exec(
        select(User).where(User.username == "master_tester")
    ).one_or_none()
    if user is None:
        user_create = UserCreate(
            username="master_tester",
            email="master@test.com",
            password=get_password_hash("testing"),
        )
        user = User.model_validate(user_create)
        user.disabled = False
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        user.api_key = get_password_hash(TEST_USER_API_KEY)
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

    yield user


@pytest.fixture(scope="function")
def api_key() -> Generator[str, None, None]:
    yield TEST_USER_API_KEY
