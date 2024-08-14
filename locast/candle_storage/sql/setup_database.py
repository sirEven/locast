from sqlalchemy import Engine
from sqlmodel import SQLModel


def create_db_and_tables(engine: Engine):
    SQLModel.metadata.create_all(engine)
