
from sqlmodel import Session, SQLModel, create_engine

# PASSWORD IS "testing_pw"

DATABASE_URL = "postgresql://postgres:testing_pw@localhost/frc_vision_testing"
# connect_args = {"check_same_thread": False}
connect_args = {}

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    SQLModel.metadata.create_all(engine)
