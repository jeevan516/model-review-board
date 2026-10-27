"""Model Review Board: a small Flask app for reviewing model predictions."""

import os

import click
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def database_url() -> str:
    """Return the database URL from DATABASE_URL, defaulting to local SQLite.

    Render hands out URLs starting with postgres:// or postgresql://, which
    SQLAlchemy would pair with psycopg2. This app installs psycopg (version 3),
    so the scheme is rewritten to name that driver explicitly.
    """
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        # A relative SQLite path resolves to Flask's instance/ folder.
        return "sqlite:///reviews.db"
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix) :]
    return url


def create_app(test_config: dict | None = None) -> Flask:
    """Create and configure the Flask application."""
    load_dotenv()

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-not-secret"),
        SQLALCHEMY_DATABASE_URI=database_url(),
        # Drop dead connections instead of failing the next request.
        SQLALCHEMY_ENGINE_OPTIONS={"pool_pre_ping": True},
    )
    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)

    from . import models  # noqa: F401  (registers the Review table)
    from .routes import bp

    app.register_blueprint(bp)
    register_commands(app)
    return app


def register_commands(app: Flask) -> None:
    """Add the init-db and seed-db commands to the flask CLI."""

    @app.cli.command("init-db")
    def init_db() -> None:
        """Create the reviews table if it does not exist yet."""
        db.create_all()
        click.echo("Database initialised.")

    @app.cli.command("seed-db")
    def seed_db() -> None:
        """Add three sample reviews for local development."""
        from .models import Review

        db.create_all()
        db.session.add_all(
            [
                Review(
                    case_reference="CASE-001",
                    prediction="fraud",
                    confidence=0.91,
                    input_summary="Card payment of 2,400 EUR from a new device abroad.",
                ),
                Review(
                    case_reference="CASE-002",
                    prediction="not fraud",
                    confidence=0.64,
                    input_summary="Recurring utility payment, amount 15% above usual.",
                    decision="approved",
                    notes="Matches the customer's seasonal pattern.",
                ),
                Review(
                    case_reference="CASE-003",
                    prediction="fraud",
                    confidence=0.52,
                    input_summary="Three small online purchases within two minutes.",
                    decision="rejected",
                    notes="Customer confirmed the purchases by phone.",
                ),
            ]
        )
        db.session.commit()
        click.echo("Added 3 sample reviews.")
