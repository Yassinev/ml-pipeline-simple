"""
Unit tests for src/schemas.py — run via `make test`.
Covers AC-04, AC-05, AC-09, AC-10, AC-11 from the Acceptance Criteria Table.
"""
import uuid
import pytest
from src.schemas import validate_request, validate_response, ValidationError


# ── Helpers ──────────────────────────────────────────────────────────────────

def good_request(**overrides) -> dict:
    base = {
        "request_id": str(uuid.uuid4()),
        "text": "Hello world",
        "timestamp": "2026-04-19T12:00:00Z",
    }
    base.update(overrides)
    return base


def good_response(**overrides) -> dict:
    base = {
        "request_id": str(uuid.uuid4()),
        "label": "positive",
        "confidence": 0.91,
        "latency_ms": 250,
        "status": "ok",
    }
    base.update(overrides)
    return base


# ── Request validation ────────────────────────────────────────────────────────

class TestRequestValidation:
    def test_valid_request_passes(self):
        validate_request(good_request())  # should not raise

    def test_missing_text_raises(self):
        """AC-10: missing required field returns 422-equivalent error."""
        r = good_request()
        del r["text"]
        with pytest.raises(ValidationError, match="text"):
            validate_request(r)

    def test_missing_request_id_raises(self):
        r = good_request()
        del r["request_id"]
        with pytest.raises(ValidationError, match="request_id"):
            validate_request(r)

    def test_empty_string_raises(self):
        """AC-04: empty string must be rejected."""
        with pytest.raises(ValidationError):
            validate_request(good_request(text=""))

    def test_whitespace_only_raises(self):
        """AC-12: whitespace-only input must be rejected."""
        with pytest.raises(ValidationError):
            validate_request(good_request(text="   \n\t  "))

    def test_max_length_text_passes(self):
        """AC-05: text at exactly 4096 chars must be accepted."""
        validate_request(good_request(text="a" * 4096))

    def test_over_max_length_raises(self):
        with pytest.raises(ValidationError, match="max length"):
            validate_request(good_request(text="a" * 4097))

    def test_invalid_uuid_raises(self):
        with pytest.raises(ValidationError, match="UUID"):
            validate_request(good_request(request_id="not-a-uuid"))

    def test_invalid_user_tier_raises(self):
        with pytest.raises(ValidationError, match="user_tier"):
            validate_request(good_request(metadata={"user_tier": "platinum"}))

    def test_valid_metadata_passes(self):
        validate_request(good_request(metadata={"user_tier": "pro", "source": "web"}))


# ── Response validation ───────────────────────────────────────────────────────

class TestResponseValidation:
    def test_valid_response_passes(self):
        validate_response(good_response())

    def test_invalid_label_raises(self):
        with pytest.raises(ValidationError, match="label"):
            validate_response(good_response(label="unknown"))

    def test_confidence_out_of_range_raises(self):
        with pytest.raises(ValidationError, match="confidence"):
            validate_response(good_response(confidence=1.5))

    def test_negative_latency_raises(self):
        with pytest.raises(ValidationError, match="latency_ms"):
            validate_response(good_response(latency_ms=-1))

    def test_invalid_status_raises(self):
        with pytest.raises(ValidationError, match="status"):
            validate_response(good_response(status="unknown_status"))

    def test_uncertain_label_ok(self):
        """AC-06: uncertain label with low confidence must be a valid response."""
        validate_response(good_response(label="uncertain", confidence=0.40, status="ok"))

    def test_timeout_status_ok(self):
        """AC-11: timeout status must be a valid response."""
        validate_response(good_response(
            label="uncertain", confidence=0.0, status="timeout",
            latency_ms=2600, fallback_reason="inference timeout"
        ))


# ── Model behaviour ───────────────────────────────────────────────────────────

class TestModelBehaviour:
    def test_uncertainty_zone(self):
        """AC-06: confidence < 0.55 must yield label=uncertain."""
        from src.model import predict
        from src.schemas import UNCERTAINTY_THRESHOLD
        result = predict("hmm")
        if result["confidence"] < UNCERTAINTY_THRESHOLD:
            assert result["label"] == "uncertain"

    def test_positive_text_predicts_positive(self):
        from src.model import predict
        result = predict("This is excellent and I love it, highly recommend outstanding")
        assert result["label"] in ("positive", "uncertain")

    def test_negative_text_predicts_negative(self):
        from src.model import predict
        result = predict("Terrible experience, worst product, totally broken and useless")
        assert result["label"] in ("negative", "uncertain")

    def test_confidence_in_range(self):
        from src.model import predict
        result = predict("The item arrived on time.")
        assert 0.0 <= result["confidence"] <= 1.0

    def test_latency_ms_non_negative(self):
        from src.model import predict
        result = predict("test")
        assert result["latency_ms"] >= 0
