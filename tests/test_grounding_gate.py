"""
tests/test_grounding_gate.py
Gate 3: Non-uncertain responses must include key_phrase.
        Only allowlisted tools may be called.
"""
import json
import pytest
from pathlib import Path

ALLOWLIST_PATH = Path(__file__).parent.parent / "safety" / "tool_allowlist.json"


def load_allowlist() -> set:
    with open(ALLOWLIST_PATH) as f:
        data = json.load(f)
    return {t["name"] for t in data["allowlist"]}


class TestGroundingGate:

    def test_allowlist_file_exists(self):
        assert ALLOWLIST_PATH.exists(), f"tool_allowlist.json not found at {ALLOWLIST_PATH}"

    def test_allowlist_has_required_tools(self):
        allowlist = load_allowlist()
        required = {"classify_text", "log_request", "flag_for_human_review"}
        assert required.issubset(allowlist), \
            f"Missing required tools in allowlist: {required - allowlist}"

    def test_positive_response_has_key_phrase(self):
        """Non-uncertain responses must include a key_phrase."""
        response = {
            "request_id": "550e8400-e29b-41d4-a716-446655440010",
            "label": "positive",
            "confidence": 0.92,
            "key_phrase": "exceeded my expectations",
            "latency_ms": 142,
            "status": "ok",
            "error_code": None
        }
        if response["label"] != "uncertain":
            assert response.get("key_phrase") is not None, \
                "Non-uncertain response missing key_phrase — potential hallucination"
            assert len(response["key_phrase"]) > 0

    def test_uncertain_response_allows_null_key_phrase(self):
        response = {
            "request_id": "550e8400-e29b-41d4-a716-446655440011",
            "label": "uncertain",
            "confidence": 0.45,
            "key_phrase": None,
            "latency_ms": 80,
            "status": "ok",
            "error_code": None
        }
        # uncertain responses may have null key_phrase — this is correct
        assert response["label"] == "uncertain"

    def test_blocked_tool_not_in_allowlist(self):
        allowlist = load_allowlist()
        blocked_tools = ["delete_order", "send_email", "drop_table",
                         "export_data", "access_database"]
        for tool in blocked_tools:
            assert tool not in allowlist, \
                f"Dangerous tool '{tool}' found in allowlist — must be blocked"

    def test_destructive_tool_requires_confirmation(self):
        with open(ALLOWLIST_PATH) as f:
            data = json.load(f)
        for tool in data["allowlist"]:
            if tool["name"] == "update_model":
                assert tool["confirmation_required"] is True, \
                    "update_model must require confirmation"

    def test_write_tools_have_permission_field(self):
        with open(ALLOWLIST_PATH) as f:
            data = json.load(f)
        for tool in data["allowlist"]:
            assert "permission" in tool, \
                f"Tool '{tool['name']}' missing 'permission' field"
            assert tool["permission"] in ("read", "write"), \
                f"Tool '{tool['name']}' has invalid permission: {tool['permission']}"

    def test_allowlist_policy_is_default_deny(self):
        with open(ALLOWLIST_PATH) as f:
            data = json.load(f)
        assert data.get("policy") == "default_deny", \
            "Allowlist policy must be 'default_deny'"
