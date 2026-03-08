"""
Data Contract Validator
Validates data/sample_requests.jsonl against the schema defined in specs/DataSpec.md.
Exits with code 1 if any ERROR-level rule is violated.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

ALLOWED_LABELS = {"positive", "negative", "neutral", "unknown"}

HARD_GATE_RULES = []  # populated via check functions
violations: list[str] = []
warnings: list[str] = []


def check_record(i: int, record: dict) -> None:
    required_fields = ["id", "input_text", "label", "score", "timestamp"]
    for field in required_fields:
        if field not in record or record[field] is None:
            violations.append(f"Record {i}: DQ-01 missing required field '{field}'")

    if "score" in record and record["score"] is not None:
        try:
            s = float(record["score"])
            if not (0.0 <= s <= 1.0):
                violations.append(f"Record {i}: DQ-02 score={s} out of range [0, 1]")
        except (ValueError, TypeError):
            violations.append(f"Record {i}: DQ-02 score is not a valid float")

    if "label" in record and record["label"] is not None:
        if record["label"] not in ALLOWED_LABELS:
            violations.append(
                f"Record {i}: DQ-03 label='{record['label']}' not in allowed set {ALLOWED_LABELS}"
            )

    if "input_text" in record and record["input_text"] is not None:
        if len(str(record["input_text"])) < 1:
            violations.append(f"Record {i}: DQ-05 input_text is empty")

    if "timestamp" in record and record["timestamp"] is not None:
        try:
            datetime.fromisoformat(str(record["timestamp"]).replace("Z", "+00:00"))
        except ValueError:
            warnings.append(f"Record {i}: DQ-06 timestamp is not valid ISO-8601")


def main() -> int:
    data_path = Path("data/sample_requests.jsonl")
    if not data_path.exists():
        print(f"ERROR: Data file not found: {data_path}", file=sys.stderr)
        return 1

    records = []
    with data_path.open() as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                records.append(record)
                check_record(i, record)
            except json.JSONDecodeError as e:
                violations.append(f"Line {i}: invalid JSON — {e}")

    # DQ-04: unique IDs
    ids = [r.get("id") for r in records if r.get("id") is not None]
    if len(ids) != len(set(ids)):
        from collections import Counter
        dupes = [id_ for id_, count in Counter(ids).items() if count > 1]
        violations.append(f"DQ-04 duplicate IDs found: {dupes}")

    # Report
    print(f"✅ Records checked: {len(records)}")
    if warnings:
        print(f"⚠️  Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"   {w}")
    if violations:
        print(f"❌ Violations ({len(violations)}):")
        for v in violations:
            print(f"   {v}")
        return 1

    print("✅ Data contract check PASSED — no violations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
