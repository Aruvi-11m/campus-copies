"""
Campus Copies ERP - Database Session & Engine Configuration

Configures SQLAlchemy 2.x with NullPool for Supabase PgBouncer Transaction Mode.
Grounding: docs/BackendSpecification.md §2, docs/Architecture.md §18
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import NullPool

from app.config import settings
from app.core.logging import logger


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy 2.x ORM models."""

    pass


# Create engine with NullPool to prevent prepared statement errors in PgBouncer Transaction Mode
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=NullPool,
    pool_pre_ping=True,
    echo=(settings.LOG_LEVEL.upper() == "DEBUG"),
)

# SessionFactory for database sessions
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding a SQLAlchemy session per request.
    Ensures session clean close upon request completion.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as exc:
        logger.error("database_session_exception_rollback", error=str(exc))
        db.rollback()
        raise
    finally:
        db.close()
