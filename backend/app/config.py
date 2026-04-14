"""
Configuration management for the Liver Function Report Analyzer application.
Loads settings from environment variables with sensible defaults.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration class."""

    # Flask settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    FLASK_ENV: str = os.getenv("FLASK_ENV", "production")

    # File upload settings
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "/tmp/uploads")
    MAX_CONTENT_LENGTH: int = int(os.getenv("MAX_CONTENT_LENGTH", str(16 * 1024 * 1024)))  # 16 MB
    ALLOWED_EXTENSIONS: set = {"pdf", "jpg", "jpeg", "png"}

    # OpenAI settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))

    # Local LLM settings (alternative to OpenAI)
    USE_LOCAL_LLM: bool = os.getenv("USE_LOCAL_LLM", "False").lower() == "true"
    LOCAL_LLM_URL: str = os.getenv("LOCAL_LLM_URL", "http://localhost:11434")
    LOCAL_LLM_MODEL: str = os.getenv("LOCAL_LLM_MODEL", "llama3")

    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///liver_analyzer.db")
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # OCR settings
    OCR_LANGUAGE: str = os.getenv("OCR_LANGUAGE", "ch")  # 'ch' for Chinese+English
    OCR_USE_GPU: bool = os.getenv("OCR_USE_GPU", "False").lower() == "true"

    # Analysis settings
    ANALYSIS_LANGUAGE: str = os.getenv("ANALYSIS_LANGUAGE", "zh")  # 'zh' for Chinese


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    FLASK_ENV = "development"


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    FLASK_ENV = "production"


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    DEBUG = True
    DATABASE_URL = "sqlite:///:memory:"
    UPLOAD_FOLDER = "/tmp/test_uploads"


# Map environment names to configuration classes
config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config() -> Config:
    """Return the appropriate configuration object based on FLASK_ENV."""
    env = os.getenv("FLASK_ENV", "development")
    return config_map.get(env, config_map["default"])()
