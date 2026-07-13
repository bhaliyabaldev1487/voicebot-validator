from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def create_session_factory(connection_url: str, echo: bool = False):
    """
    Returns a SQLAlchemy session factory.
    """
    engine = create_engine(
        connection_url,
        echo=echo,
        future=True,
        pool_pre_ping=True,
    )

    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )