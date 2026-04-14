"""
Flask application entry point.

Creates and configures the Flask app and registers all blueprints.
"""

from __future__ import annotations

import logging
import os

from flask import Flask, g, jsonify
from flask_cors import CORS

from .config import get_config
from .routes.reports import reports_bp

logger = logging.getLogger(__name__)


def create_app(config=None) -> Flask:
    """
    Application factory.

    Args:
        config: Optional configuration object. Defaults to reading from env.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)

    # Load configuration
    if config is None:
        config = get_config()
    app.config.from_object(config)

    # Ensure upload folder exists
    upload_folder = app.config.get("UPLOAD_FOLDER", "/tmp/uploads")
    os.makedirs(upload_folder, exist_ok=True)

    # Enable CORS for all routes
    CORS(app)

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if app.config.get("DEBUG") else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # ------------------------------------------------------------------
    # Database initialisation
    # ------------------------------------------------------------------
    from .database import check_connection, create_all_tables, init_engine

    db_url = app.config.get("DATABASE_URL", "sqlite:///liver_analyzer.db")
    db_echo = app.config.get("DATABASE_ECHO", False)
    init_engine(db_url, echo=db_echo)
    create_all_tables()

    # Per-request session teardown
    @app.teardown_appcontext
    def _close_db_session(exc: BaseException | None) -> None:
        session = g.pop("db_session", None)
        if session is not None:
            if exc is not None:
                session.rollback()
            session.close()

    # Register blueprints
    app.register_blueprint(reports_bp)

    # ------------------------------------------------------------------
    # Health check endpoint
    # ------------------------------------------------------------------
    @app.route("/api/health", methods=["GET"])
    def health():
        db_ok = check_connection()
        return jsonify({
            "status": "healthy",
            "message": "Liver Function Report Analyzer API is running",
            "database": "connected" if db_ok else "unavailable",
        })

    # Development-only: database admin endpoints
    if app.config.get("DEBUG") or app.config.get("FLASK_ENV") == "development":
        from .database import drop_all_tables

        @app.route("/api/admin/db/init", methods=["POST"])
        def db_init():
            create_all_tables()
            return jsonify({"status": "ok", "message": "Tables created."})

        @app.route("/api/admin/db/reset", methods=["POST"])
        def db_reset():
            drop_all_tables()
            create_all_tables()
            return jsonify({"status": "ok", "message": "Database reset."})

    logger.info("Flask app created (env=%s)", app.config.get("FLASK_ENV"))
    return app
