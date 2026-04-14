"""
Flask application entry point.

Creates and configures the Flask app and registers all blueprints.
"""

from __future__ import annotations

import logging
import os

from flask import Flask, jsonify
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

    # Register blueprints
    app.register_blueprint(reports_bp)

    # Health check endpoint
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "healthy",
            "message": "Liver Function Report Analyzer API is running",
        })

    logger.info("Flask app created (env=%s)", app.config.get("FLASK_ENV"))
    return app
