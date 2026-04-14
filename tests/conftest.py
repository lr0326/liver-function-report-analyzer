"""
Pytest configuration and shared fixtures for the test suite.
"""

import sys
import os

# Allow imports from the backend package without installation
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from app.main import create_app
from app.config import TestingConfig


@pytest.fixture()
def app():
    """Create a Flask test application."""
    application = create_app(TestingConfig())
    application.config["TESTING"] = True
    return application


@pytest.fixture()
def client(app):
    """Return a Flask test client."""
    return app.test_client()
