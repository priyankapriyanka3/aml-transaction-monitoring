"""Database engine, session, and base model configuration."""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from .config import settings


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# Create sync engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.debug
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)


def get_db() -> Generator[Session, None, None]:
    """Dependency that provides a database session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    """Initialize database - create all tables.
    
    Note: In production, use Alembic migrations instead.
    This is provided for testing and initial development only.
    """
    import app.models  # noqa: F401 - Import models to register them with Base
    Base.metadata.create_all(bind=engine)
