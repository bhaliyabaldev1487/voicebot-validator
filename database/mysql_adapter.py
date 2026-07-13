from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def create_session_factory(connection_url: str, echo: bool = False):
    engine = create_engine(connection_url, echo=echo, future=True)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)