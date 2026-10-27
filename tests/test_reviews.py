from unittest.mock import patch

import pytest
from sqlalchemy.exc import OperationalError

from app import database_url, db
from app.models import Review

from .conftest import VALID_FORM


# Dashboard


def test_dashboard_empty_state(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"No reviews yet" in response.data
    assert b"Create the first review" in response.data


def test_dashboard_lists_reviews_and_totals(client, review):
    db.session.add(
        Review(
            case_reference="CASE-101",
            prediction="fraud",
            confidence=0.4,
            input_summary="Small purchase.",
            decision="approved",
        )
    )
    db.session.commit()

    html = client.get("/").get_data(as_text=True)
    assert "CASE-100" in html
    assert "CASE-101" in html
    assert 'id="total-total">2<' in html
    assert 'id="total-pending">1<' in html
    assert 'id="total-approved">1<' in html
    assert 'id="total-rejected">0<' in html


def test_dashboard_filters_by_decision(client, review):
    db.session.add(
        Review(
            case_reference="CASE-102",
            prediction="fraud",
            confidence=0.9,
            input_summary="Card used in two countries.",
            decision="rejected",
        )
    )
    db.session.commit()

    html = client.get("/?status=rejected").get_data(as_text=True)
    assert "CASE-102" in html
    assert "CASE-100" not in html
    # Totals still describe every review, not just the filtered ones.
    assert 'id="total-total">2<' in html

    assert "No approved reviews" in client.get("/?status=approved").get_data(as_text=True)
    # An unknown status falls back to showing everything.
    assert "CASE-100" in client.get("/?status=bogus").get_data(as_text=True)


def test_dashboard_search(client, review):
    db.session.add(
        Review(
            case_reference="Priya Sharma",
            prediction="shortlist for Data Analyst",
            confidence=0.8,
            input_summary="Applicant for Data Analyst; 4 yrs experience, skills: SQL, Excel.",
            decision="approved",
        )
    )
    db.session.commit()

    # Matches name, prediction and summary, ignoring case.
    for term in ("priya", "DATA ANALYST", "sql"):
        html = client.get(f"/?q={term}").get_data(as_text=True)
        assert "Priya Sharma" in html
        assert "CASE-100" not in html

    # Search combines with the decision filter.
    assert "No reviews match" in client.get("/?q=priya&status=rejected").get_data(as_text=True)
    # % is matched literally, not as a wildcard.
    assert "No reviews match" in client.get("/?q=%25").get_data(as_text=True)


def test_avatar_initials(client, review):
    db.session.add(
        Review(case_reference="Priya Sharma", prediction="x", confidence=0.5, input_summary="x")
    )
    db.session.commit()
    html = client.get("/").get_data(as_text=True)
    assert ">PS</span>" in html
    assert ">C1</span>" in html  # CASE-100


# Create and validation


def test_create_review(client):
    response = client.post("/reviews/new", data=VALID_FORM, follow_redirects=True)
    assert response.status_code == 200
    assert b"Review CASE-200 created." in response.data

    saved = db.session.scalars(db.select(Review)).one()
    assert saved.case_reference == "CASE-200"
    assert saved.confidence == 0.75
    assert saved.decision == "pending"


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("case_reference", "", "Case reference is required."),
        ("prediction", "   ", "Prediction is required."),
        ("input_summary", "", "Input summary is required."),
        ("confidence", "", "Confidence is required."),
        ("confidence", "high", "Confidence must be a number"),
        ("confidence", "1.5", "Confidence must be between 0 and 1."),
        ("confidence", "-0.1", "Confidence must be between 0 and 1."),
        ("confidence", "nan", "Confidence must be between 0 and 1."),
        ("decision", "maybe", "Decision must be pending, approved or rejected."),
        ("case_reference", "X" * 65, "at most 64 characters"),
    ],
)
def test_create_rejects_invalid_input(client, field, value, message):
    response = client.post("/reviews/new", data={**VALID_FORM, field: value})
    assert response.status_code == 400
    assert message in response.get_data(as_text=True)
    assert db.session.scalars(db.select(Review)).first() is None


def test_invalid_form_keeps_entered_values(client):
    response = client.post("/reviews/new", data={**VALID_FORM, "confidence": "2"})
    assert 'value="CASE-200"' in response.get_data(as_text=True)


def test_confidence_boundaries_are_allowed(client):
    for value in ("0", "1"):
        form = {**VALID_FORM, "case_reference": f"EDGE-{value}", "confidence": value}
        assert client.post("/reviews/new", data=form).status_code == 302


# Read and edit


def test_detail_page_shows_saved_decision(client, review):
    response = client.get(f"/reviews/{review.id}")
    assert response.status_code == 200
    assert b"CASE-100" in response.data


def test_missing_review_returns_404(client):
    assert client.get("/reviews/999").status_code == 404


def test_edit_updates_decision_and_notes(client, review):
    form = {
        **VALID_FORM,
        "case_reference": "CASE-100",
        "decision": "approved",
        "notes": "Checked with the account owner.",
    }
    response = client.post(f"/reviews/{review.id}/edit", data=form, follow_redirects=True)
    assert response.status_code == 200
    assert b"saved as approved" in response.data

    # A separate client stands in for another reviewer's browser session.
    other_browser = client.application.test_client()
    html = other_browser.get(f"/reviews/{review.id}").get_data(as_text=True)
    assert "approved" in html
    assert "Checked with the account owner." in html


def test_edit_rejects_invalid_decision(client, review):
    form = {**VALID_FORM, "decision": "deleted"}
    response = client.post(f"/reviews/{review.id}/edit", data=form)
    assert response.status_code == 400
    db.session.refresh(review)
    assert review.decision == "pending"


# Delete


def test_delete_requires_post(client, review):
    response = client.get(f"/reviews/{review.id}/delete")
    assert response.status_code == 200
    assert b"Delete review CASE-100?" in response.data
    assert db.session.get(Review, review.id) is not None


def test_delete_review(client, review):
    review_id = review.id
    response = client.post(f"/reviews/{review_id}/delete", follow_redirects=True)
    assert response.status_code == 200
    assert b"Review CASE-100 deleted." in response.data
    assert db.session.get(Review, review_id) is None


# Health


def test_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "database": "ok"}


def test_health_reports_database_failure(client):
    error = OperationalError("SELECT 1", {}, Exception("connection refused"))
    with patch.object(db.session, "execute", side_effect=error):
        response = client.get("/health")
    assert response.status_code == 503
    assert response.get_json()["database"] == "unreachable"


# Configuration


@pytest.mark.parametrize(
    ("env_value", "expected"),
    [
        ("", "sqlite:///reviews.db"),
        ("postgres://u:p@host/db", "postgresql+psycopg://u:p@host/db"),
        ("postgresql://u:p@host/db", "postgresql+psycopg://u:p@host/db"),
    ],
)
def test_database_url(monkeypatch, env_value, expected):
    monkeypatch.setenv("DATABASE_URL", env_value)
    assert database_url() == expected
