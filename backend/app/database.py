"""
Database configuration and session management.

Supports PostgreSQL (production) and SQLite (development/testing).
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Declarative base – all ORM models inherit from this
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    """Base class for all ORM models."""


# ---------------------------------------------------------------------------
# Module-level state (populated by init_db / create_app)
# ---------------------------------------------------------------------------

_engine = None
_SessionFactory: sessionmaker | None = None


def init_engine(database_url: str, echo: bool = False):
    """
    Create the SQLAlchemy engine and session factory.

    Args:
        database_url: SQLAlchemy connection URL.
        echo: If True, emit SQL statements to the logger.
    """
    global _engine, _SessionFactory

    connect_args = {}
    if database_url.startswith("sqlite"):
        # Required for SQLite when used across threads (e.g. Flask dev server)
        connect_args["check_same_thread"] = False

    _engine = create_engine(
        database_url,
        echo=echo,
        pool_pre_ping=True,
        connect_args=connect_args,
    )

    # Enable WAL mode for SQLite to improve concurrent read performance
    if database_url.startswith("sqlite"):

        @event.listens_for(_engine, "connect")
        def _set_sqlite_pragma(dbapi_conn, _connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.close()

    _SessionFactory = sessionmaker(bind=_engine, autoflush=False, autocommit=False)

    logger.info("Database engine initialised: %s", database_url.split("@")[-1])
    return _engine


def get_engine():
    """Return the current engine, raising if not initialised."""
    if _engine is None:
        raise RuntimeError(
            "Database engine has not been initialised. "
            "Call init_engine() or use create_app() first."
        )
    return _engine


def get_session_factory() -> sessionmaker:
    """Return the session factory, raising if not initialised."""
    if _SessionFactory is None:
        raise RuntimeError(
            "Session factory has not been initialised. "
            "Call init_engine() or use create_app() first."
        )
    return _SessionFactory


def get_db() -> Session:
    """
    Create and return a new database session.

    The caller is responsible for closing the session (or use
    ``db_session()`` context manager instead).
    """
    return get_session_factory()()


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """
    Context manager that yields a database session and handles
    commit / rollback automatically.

    Usage::

        with db_session() as session:
            user = session.get(User, user_id)
    """
    session: Session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_all_tables():
    """Create all tables defined in the ORM models."""
    # Import models so their metadata is registered on Base
    from app.models import user, report, analysis_result, health_record  # noqa: F401

    Base.metadata.create_all(bind=get_engine())
    logger.info("All database tables created.")


def drop_all_tables():
    """Drop all tables (useful for test teardown / reset)."""
    from app.models import user, report, analysis_result, health_record  # noqa: F401

    Base.metadata.drop_all(bind=get_engine())
    logger.warning("All database tables dropped.")


def check_connection() -> bool:
    """Return True if the database is reachable, False otherwise."""
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.error("Database connection check failed: %s", exc)
        return False
