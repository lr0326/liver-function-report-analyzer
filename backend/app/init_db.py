"""
Database initialisation helpers.

Usage (from the backend/ directory)::

    python -m app.init_db          # create all tables
    python -m app.init_db --drop   # drop then recreate all tables
    python -m app.init_db --seed   # create tables + insert seed data
"""

from __future__ import annotations

import logging
import sys

logger = logging.getLogger(__name__)


def init_db(database_url: str | None = None, echo: bool = False) -> None:
    """
    Initialise the database engine and create all tables.

    Args:
        database_url: SQLAlchemy URL. Falls back to the value from config.
        echo: Enable SQL echo for debugging.
    """
    from app.config import get_config
    from app.database import create_all_tables, init_engine

    if database_url is None:
        database_url = get_config().DATABASE_URL

    init_engine(database_url, echo=echo)
    create_all_tables()
    logger.info("Database initialised successfully.")


def drop_db(database_url: str | None = None) -> None:
    """Drop all tables (destructive – use only in development/tests)."""
    from app.config import get_config
    from app.database import drop_all_tables, get_engine, init_engine

    if database_url is None:
        database_url = get_config().DATABASE_URL

    try:
        get_engine()  # already initialised
    except RuntimeError:
        init_engine(database_url)

    drop_all_tables()
    logger.warning("All database tables have been dropped.")


def reset_db(database_url: str | None = None) -> None:
    """Drop then recreate all tables."""
    drop_db(database_url)
    init_db(database_url)
    logger.info("Database reset complete.")


def seed_db() -> None:
    """Insert a small set of seed / demo records for development."""
    from app.database import db_session
    from app.models.user import Gender, User

    logger.info("Seeding database with demo data…")

    with db_session() as session:
        # Skip if there is already at least one user
        if session.query(User).first() is not None:
            logger.info("Seed data already present – skipping.")
            return

        demo_user = User(
            username="demo_user",
            email="demo@example.com",
            full_name="Demo User",
            age=35,
            gender=Gender.Male,
        )
        demo_user.set_password("demo_password")
        session.add(demo_user)

    logger.info("Demo user created (username=demo_user, password=demo_password).")


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    args = set(sys.argv[1:])
    if "--drop" in args:
        reset_db()
    elif "--seed" in args:
        init_db()
        seed_db()
    else:
        init_db()
