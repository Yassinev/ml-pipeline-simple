# Data Specification & Data Contract
**Project:** ML Pipeline Sample  
**Version:** 1.0  
**Date:** 2026-03-08  
**Status:** Draft

---

## 1. Dataset Overview

| Property | Value |
|----------|-------|
| Format | JSONL (one JSON object per line) |
| Location | `data/sample_requests.jsonl` |
| Update Frequency | Per pipeline run |
| Owner | ML Team |

## 2. Schema Definition

Each record in the JSONL file MUST conform to the following schema:

```json
{
  "id":          "string   — unique record identifier (UUID or slug)",
  "input_text":  "string   — raw input text, 1–2048 characters",
  "label":       "string   — ground-truth label from allowed set",
  "score":       "float    — confidence or relevance score in [0.0, 1.0]",
  "timestamp":   "string   — ISO-8601 datetime, e.g. 2026-03-08T10:00:00Z"
}
```

## 3. Field Constraints

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `id` | string | ✅ | Non-empty, unique within file |
| `input_text` | string | ✅ | Length: 1–2048 chars |
| `label` | string | ✅ | Must be in allowed label set |
| `score` | float | ✅ | Range: [0.0, 1.0] |
| `timestamp` | string | ✅ | Valid ISO-8601 format |

### 3.1 Allowed Label Set
```
["positive", "negative", "neutral", "unknown"]
```

## 4. Data Quality Rules

| Rule ID | Description | Severity |
|---------|-------------|----------|
| DQ-01 | No record may have a null/missing required field | ERROR |
| DQ-02 | `score` must be within [0.0, 1.0] | ERROR |
| DQ-03 | `label` must be in the allowed set | ERROR |
| DQ-04 | `id` must be unique across all records | ERROR |
| DQ-05 | `input_text` length must be ≥ 1 | ERROR |
| DQ-06 | `timestamp` must parse as ISO-8601 | WARNING |

## 5. Data Contract

The data contract is enforced programmatically by `src/aispec/data_contract.py`.  
The validator exits with code `1` if any ERROR-level rule is violated.

### Contract Guarantees to Downstream
- All delivered records have non-null required fields.
- All `score` values are valid floats in [0, 1].
- All `label` values belong to the allowed set.

### Contract Obligations of Upstream
- Producer must validate data before writing to `data/`.
- Schema changes require a version bump and spec update.

## 6. Data Lineage

```
Raw Source → Preprocessing Script → data/sample_requests.jsonl → Data Validator → Pipeline
```

## 7. Privacy & Compliance

- Input data must be anonymized before storage.
- No PII (names, emails, phone numbers) in `input_text`.
- Data retention: 90 days unless otherwise specified.

## 8. Versioning

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-08 | Initial schema definition |
