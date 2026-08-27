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
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
