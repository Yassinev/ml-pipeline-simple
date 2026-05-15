"""
Input / Output schema definitions and validators.
Matches the schemas declared in specs/SRS_LITE.md.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Literal, Optional

# ---------------------------------------------------------------------------
# Lightweight dataclass-style schemas (no external deps beyond stdlib)
# ---------------------------------------------------------------------------

VALID_LABELS: tuple[str, ...] = ("positive", "negative", "neutral", "uncertain")
VALID_STATUSES: tuple[str, ...] = ("ok", "fallback", "timeout", "error")
VALID_TIERS: tuple[str, ...] = ("free", "pro", "enterprise")
VALID_SOURCES: tuple[str, ...] = ("web", "api", "mobile", "synthetic")

MAX_TEXT_LENGTH = 4096
UNCERTAINTY_THRESHOLD = 0.55


class ValidationError(ValueError):
    """Raised when an input or output fails schema validation."""


def validate_request(data: dict) -> None:
    """Raise ValidationError if *data* does not conform to InferenceRequest schema."""
    required = {"request_id", "text", "timestamp"}
    missing = required - data.keys()
    if missing:
        raise ValidationError(f"Missing required fields: {missing}")

    text = data["text"]
    if not isinstance(text, str):
        raise ValidationError("'text' must be a string")
    if len(text.strip()) == 0:
        raise ValidationError("'text' must not be empty or whitespace-only")
    if len(text) > MAX_TEXT_LENGTH:
        raise ValidationError(f"'text' exceeds max length of {MAX_TEXT_LENGTH}")

    try:
        uuid.UUID(str(data["request_id"]))
    except ValueError:
        raise ValidationError("'request_id' must be a valid UUID")

    meta = data.get("metadata", {})
    if meta:
        tier = meta.get("user_tier")
        if tier is not None and tier not in VALID_TIERS:
            raise ValidationError(f"'user_tier' must be one of {VALID_TIERS}")
        source = meta.get("source")
        if source is not None and source not in VALID_SOURCES:
            raise ValidationError(f"'source' must be one of {VALID_SOURCES}")


def validate_response(data: dict) -> None:
    """Raise ValidationError if *data* does not conform to InferenceResponse schema."""
    required = {"request_id", "label", "confidence", "latency_ms", "status"}
    missing = required - data.keys()
    if missing:
        raise ValidationError(f"Missing required fields: {missing}")

    if data["label"] not in VALID_LABELS:
        raise ValidationError(f"'label' must be one of {VALID_LABELS}")
    if data["status"] not in VALID_STATUSES:
        raise ValidationError(f"'status' must be one of {VALID_STATUSES}")

    conf = data["confidence"]
    if not isinstance(conf, (int, float)) or not (0.0 <= conf <= 1.0):
        raise ValidationError("'confidence' must be a float in [0.0, 1.0]")

    if not isinstance(data["latency_ms"], int) or data["latency_ms"] < 0:
        raise ValidationError("'latency_ms' must be a non-negative integer")
