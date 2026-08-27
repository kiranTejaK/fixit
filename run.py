"""
run.py — Application Entry Point

Starts the Flask development server locally or runs under Gunicorn in production.
"""

import os
from app import create_app, db

app = create_app()

# Automatically create PostgreSQL tables if they do not exist
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
