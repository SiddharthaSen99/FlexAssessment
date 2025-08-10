from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from ..config import DB_PATH


class Base(DeclarativeBase):
    pass


# Use a file-based SQLite DB. check_same_thread=False to allow FastAPI background threads
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    future=True,
    echo=False,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, future=True, class_=Session
)


def create_db_and_tables() -> None:
    from . import approvals  # noqa: F401  # ensure models are imported

    Base.metadata.create_all(bind=engine)


def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
