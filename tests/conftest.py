import pytest

from app import create_app, db
from app.models import Review


@pytest.fixture()
def app():
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test",
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
        }
    )
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def review(app):
    review = Review(
        case_reference="CASE-100",
        prediction="fraud",
        confidence=0.8,
        input_summary="Large transfer to a new payee.",
    )
    db.session.add(review)
    db.session.commit()
    return review


VALID_FORM = {
    "case_reference": "CASE-200",
    "prediction": "not fraud",
    "confidence": "0.75",
    "input_summary": "Monthly rent payment.",
    "decision": "pending",
    "notes": "",
}
