import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import DATABASE_URL
from app.database import get_session
from app.main import app

# Engine just for tests
engine = create_engine(DATABASE_URL, echo=True)

@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    """Create all tables at the start of the test session, drop them at the end."""
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def test_db():
    """Provide a fresh DB session for each test."""
    with Session(engine) as session:
        yield session
        session.rollback()  # rollback after each test just in case

@pytest.fixture(scope="function")
def client(test_db):
    """
    Override FastAPI's get_session dependency to use the test session.
    """
    def override_get_db():
        yield test_db

    app.dependency_overrides[get_session] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
