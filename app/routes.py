"""Routes for the dashboard, review forms and health check."""

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from sqlalchemy import func, text
from sqlalchemy.exc import SQLAlchemyError

from . import db
from .models import DECISIONS, Review
from .validation import validate_review

bp = Blueprint("reviews", __name__)


def status_totals() -> dict[str, int]:
    """Count reviews per decision, including decisions with no reviews."""
    rows = db.session.execute(
        db.select(Review.decision, func.count()).group_by(Review.decision)
    ).all()
    totals = dict.fromkeys(DECISIONS, 0)
    totals.update({decision: count for decision, count in rows})
    totals["total"] = sum(totals[d] for d in DECISIONS)
    return totals


@bp.get("/")
def dashboard():
    reviews = db.session.scalars(
        db.select(Review).order_by(Review.created_at.desc(), Review.id.desc())
    ).all()
    return render_template("dashboard.html", reviews=reviews, totals=status_totals())


@bp.route("/reviews/new", methods=["GET", "POST"])
def create_review():
    if request.method == "GET":
        return render_template("form.html", review=None, values={}, errors={})

    data, errors = validate_review(request.form)
    if errors:
        return render_template("form.html", review=None, values=data, errors=errors), 400

    review = Review(**data)
    db.session.add(review)
    db.session.commit()
    flash(f"Review {review.case_reference} created.", "success")
    return redirect(url_for("reviews.review_detail", review_id=review.id))


@bp.get("/reviews/<int:review_id>")
def review_detail(review_id: int):
    review = db.get_or_404(Review, review_id)
    return render_template("detail.html", review=review)


@bp.route("/reviews/<int:review_id>/edit", methods=["GET", "POST"])
def edit_review(review_id: int):
    review = db.get_or_404(Review, review_id)
    if request.method == "GET":
        values = {
            "case_reference": review.case_reference,
            "prediction": review.prediction,
            "confidence": review.confidence,
            "input_summary": review.input_summary,
            "decision": review.decision,
            "notes": review.notes,
        }
        return render_template("form.html", review=review, values=values, errors={})

    data, errors = validate_review(request.form)
    if errors:
        return render_template("form.html", review=review, values=data, errors=errors), 400

    for field, value in data.items():
        setattr(review, field, value)
    db.session.commit()
    flash(f"Review {review.case_reference} saved as {review.decision}.", "success")
    return redirect(url_for("reviews.review_detail", review_id=review.id))


@bp.get("/reviews/<int:review_id>/delete")
def confirm_delete(review_id: int):
    review = db.get_or_404(Review, review_id)
    return render_template("confirm_delete.html", review=review)


@bp.post("/reviews/<int:review_id>/delete")
def delete_review(review_id: int):
    review = db.get_or_404(Review, review_id)
    db.session.delete(review)
    db.session.commit()
    flash(f"Review {review.case_reference} deleted.", "success")
    return redirect(url_for("reviews.dashboard"))


@bp.get("/health")
def health():
    try:
        db.session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        current_app.logger.exception("Health check could not reach the database")
        db.session.rollback()
        return {"status": "error", "database": "unreachable"}, 503
    return {"status": "ok", "database": "ok"}, 200
