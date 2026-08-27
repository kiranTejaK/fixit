"""
app/__init__.py — Application Factory

Initializes the Flask app and binds SQLAlchemy extensions.
"""

from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize SQLAlchemy with the Flask app
    db.init_app(app)

    # Register routes blueprint
    from app.routes import main
    app.register_blueprint(main)

    # Provide current datetime to all Jinja templates (for footer year and status math)
    @app.context_processor
    def inject_now():
        return {"now": datetime.now()}

    return app
