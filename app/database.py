from sqlalchemy.orm import Session
from sqlmodel import create_engine

DATABASE_URL = ""
# connect_args = {"check_same_thread": False}
connect_args = {}

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
