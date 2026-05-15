"""
tests/test_schema_gate.py
Gate 1: Every response must validate against Output_Schema.json
"""
import json
import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

SCHEMA_PATH = Path(__file__).parent.parent / "specs" / "Output_Schema.json"

REQUIRED_FIELDS = {"request_id", "label", "confidence", "latency_ms", "status"}
VALID_LABELS = {"positive", "negative", "neutral", "uncertain"}
VALID_STATUSES = {"ok", "fallback", "timeout", "error"}
VALID_ERROR_CODES = {"PII_DETECTED", "UNSAFE_INPUT", "EMPTY_INPUT", "INPUT_TOO_LONG", "MODEL_ERROR", None}


def validate_response(response: dict) -> list[str]:
    """Return list of validation errors. Empty list = valid."""
    errors = []
    missing = REQUIRED_FIELDS - response.keys()
    if missing:
        errors.append(f"Missing required fields: {missing}")
    if response.get("label") not in VALID_LABELS:
        errors.append(f"Invalid label: {response.get('label')}")
    if response.get("status") not in VALID_STATUSES:
        errors.append(f"Invalid status: {response.get('status')}")
    conf = response.get("confidence")
    if conf is None or not (0.0 <= float(conf) <= 1.0):
        errors.append(f"Invalid confidence: {conf}")
    if not isinstance(response.get("latency_ms"), int) or response.get("latency_ms") < 0:
        errors.append(f"Invalid latency_ms: {response.get('latency_ms')}")
    if response.get("label") == "uncertain" and float(response.get("confidence", 1.0)) > 0.55:
        errors.append("uncertain label must have confidence <= 0.55")
    if response.get("error_code") not in VALID_ERROR_CODES:
        errors.append(f"Invalid error_code: {response.get('error_code')}")
    return errors


# ── Test Cases ──────────────────────────────────────────────

class TestSchemaGate:

    def test_valid_positive_response(self):
        response = {
            "request_id": "550e8400-e29b-41d4-a716-446655440000",
            "label": "positive",
            "confidence": 0.92,
            "key_phrase": "exceeded my expectations",
            "latency_ms": 142,
            "status": "ok",
            "error_code": None,
            "requires_human_review": False,
            "model_version": "1.0.0"
        }
        assert validate_response(response) == []

    def test_valid_negative_response(self):
        response = {
            "request_id": "550e8400-e29b-41d4-a716-446655440001",
            "label": "negative",
            "confidence": 0.88,
            "key_phrase": "extremely slow",
            "latency_ms": 210,
            "status": "ok",
            "error_code": None,
            "requires_human_review": False,
            "model_version": "1.0.0"
        }
        assert validate_response(response) == []

    def test_valid_uncertain_response_low_confidence(self):
        response = {
            "request_id": "550e8400-e29b-41d4-a716-446655440002",
            "label": "uncertain",
            "confidence": 0.48,
            "key_phrase": None,
            "latency_ms": 95,
            "status": "ok",
            "error_code": None,
            "requires_human_review": True,
            "model_version": "1.0.0"
        }
        assert validate_response(response) == []

    def test_missing_required_field_fails(self):
        response = {
            "label": "positive",
            "confidence": 0.90,
            "latency_ms": 100,
            "status": "ok"
            # missing request_id
        }
        errors = validate_response(response)
        assert any("request_id" in e for e in errors)

    def test_invalid_label_fails(self):
        response = {
            "request_id": "550e8400-e29b-41d4-a716-446655440003",
            "label": "happy",  # invalid
            "confidence": 0.80,
            "latency_ms": 100,
            "status": "ok",
            "error_code": None
        }
        errors = validate_response(response)
        assert any("label" in e for e in errors)

    def test_uncertain_with_high_confidence_fails(self):
        response = {
            "request_id": "550e8400-e29b-41d4-a716-446655440004",
            "label": "uncertain",
            "confidence": 0.80,  # too high for uncertain
            "latency_ms": 100,
            "status": "ok",
            "error_code": None
        }
        errors = validate_response(response)
        assert any("uncertain" in e for e in errors)

    def test_error_response_valid(self):
        response = {
            "request_id": "550e8400-e29b-41d4-a716-446655440005",
            "label": "uncertain",
            "confidence": 0.0,
            "latency_ms": 10,
            "status": "error",
            "error_code": "PII_DETECTED",
            "requires_human_review": True,
            "model_version": "1.0.0"
        }
        assert validate_response(response) == []

    def test_schema_file_exists(self):
        assert SCHEMA_PATH.exists(), f"Output_Schema.json not found at {SCHEMA_PATH}"
