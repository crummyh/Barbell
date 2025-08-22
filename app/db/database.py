
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import DATABASE_URL

connect_args = {}

engine = create_engine(DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    SQLModel.metadata.create_all(engine)
