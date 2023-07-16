from sqlmodel import create_engine, Session
from app.config import config
from app.db.models import Base

engine = create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False})


def get_session():
    with Session(engine) as session:
        yield session
