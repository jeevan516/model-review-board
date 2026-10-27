"""Validate review form input before it reaches the database."""

import math
from collections.abc import Mapping

from .models import DECISIONS

# Field name -> (label, maximum length) for the required text fields.
REQUIRED_TEXT = {
    "case_reference": ("Case reference", 64),
    "prediction": ("Prediction", 120),
    "input_summary": ("Input summary", 500),
}
NOTES_MAX = 2000


def validate_review(form: Mapping[str, str]) -> tuple[dict, dict[str, str]]:
    """Return (cleaned values, errors). errors maps a field name to a message."""
    data: dict = {}
    errors: dict[str, str] = {}

    for field, (label, max_len) in REQUIRED_TEXT.items():
        value = form.get(field, "").strip()
        if not value:
            errors[field] = f"{label} is required."
        elif len(value) > max_len:
            errors[field] = f"{label} must be at most {max_len} characters."
        data[field] = value

    raw_confidence = form.get("confidence", "").strip()
    data["confidence"] = raw_confidence
    if not raw_confidence:
        errors["confidence"] = "Confidence is required."
    else:
        try:
            confidence = float(raw_confidence)
        except ValueError:
            errors["confidence"] = "Confidence must be a number, for example 0.85."
        else:
            if math.isnan(confidence) or not 0 <= confidence <= 1:
                errors["confidence"] = "Confidence must be between 0 and 1."
            else:
                data["confidence"] = confidence

    decision = form.get("decision", "pending").strip()
    data["decision"] = decision
    if decision not in DECISIONS:
        errors["decision"] = "Decision must be pending, approved or rejected."

    notes = form.get("notes", "").strip()
    data["notes"] = notes
    if len(notes) > NOTES_MAX:
        errors["notes"] = f"Notes must be at most {NOTES_MAX} characters."

    return data, errors
