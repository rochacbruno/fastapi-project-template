from sqlmodel import SQLModel, create_engine

from .config import settings

engine = create_engine(
    settings.db.uri, echo=True, connect_args=settings.db.connect_args
)


def create_db_and_tables(engine):
    SQLModel.metadata.create_all(engine)
