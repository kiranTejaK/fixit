"""
config.py — Application Configuration

Loads database connection and secret key from environment variables.
"""

import os
from dotenv import load_dotenv

# Load variables from .env file if present
load_dotenv()


class Config:
    # Flask secret key for session and flash messages
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-12345")

    # PostgreSQL database connection URI from DATABASE_URL
    # Render provides postgres://, which SQLAlchemy 1.4+ expects as postgresql://
    raw_db_url = os.environ.get("DATABASE_URL")
    if raw_db_url and raw_db_url.startswith("postgres://"):
        raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = raw_db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
