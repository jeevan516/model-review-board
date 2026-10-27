"""Database model for a single prediction review."""

from datetime import datetime, timezone

from . import db

DECISIONS = ("pending", "approved", "rejected")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Review(db.Model):
    """One model prediction and the reviewer's decision about it."""

    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    case_reference = db.Column(db.String(64), nullable=False)
    prediction = db.Column(db.String(120), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    input_summary = db.Column(db.String(500), nullable=False)
    decision = db.Column(db.String(16), nullable=False, default="pending")
    notes = db.Column(db.Text, nullable=False, default="")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow
    )

    def __repr__(self) -> str:
        return f"<Review {self.case_reference} {self.decision}>"
