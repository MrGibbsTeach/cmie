from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base


def get_engine(db_url: str):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return engine


def get_session_factory(db_url: str):
    engine = get_engine(db_url)
    return sessionmaker(bind=engine)
