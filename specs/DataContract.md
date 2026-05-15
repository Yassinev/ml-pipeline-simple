# DataContract — AI Spec Pack

**Version:** 1.0.0  
**Last updated:** 2026-04-19  
**Owner:** Data Engineering  
**Consumers:** ML Training, Eval Gate, Production Inference

---

## 1. Contract Overview

This document is a binding contract between the data producer and all downstream consumers. Any change that breaks a MUST requirement requires a version bump and migration notice ≥ 7 days in advance.

---

## 2. Schema Contract

### 2.1 Training / Eval CSV

```
id,text,label,source,confidence_gt
```

| Field | Type | Nullable | Constraint |
|---|---|---|---|
| `id` | string | No | Globally unique; format `[a-z0-9-]{8,36}` |
| `text` | string | No | `len(strip()) ≥ 1`; `len ≤ 4096` |
| `label` | string | No | One of `positive`, `negative`, `neutral` |
| `source` | string | Yes | One of `web`, `api`, `mobile`, `synthetic` |
| `confidence_gt` | float | Yes | In [0.0, 1.0] |

### 2.2 Golden Set JSONL

Each line is a JSON object:

```json
{
  "id": "abc-001",
  "text": "The product exceeded all expectations.",
  "label": "positive",
  "confidence_gt": 0.95
}
```

---

## 3. SLA / Freshness

| Dataset | Max Staleness | Delivery Channel | Failure Action |
|---|---|---|---|
| `sample_train.csv` | 30 days | Git LFS / S3 | Pause training; alert Data Eng |
| `sample_val.csv` | 30 days | Git LFS / S3 | Pause eval; alert Data Eng |
| `golden_set.jsonl` | 90 days | Committed to repo | Block eval-gate; open ticket |

---

## 4. Breaking vs Non-Breaking Changes

### Breaking (requires major version bump + migration notice)
- Removing or renaming any existing column
- Changing a column's type
- Adding a new required (non-nullable) column without default
- Changing allowed values of `label`

### Non-Breaking (minor version bump OK)
- Adding a new optional column
- Expanding allowed values of `source`
- Adding rows / samples

---

## 5. Change Log

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0.0 | 2026-04-19 | Project Init | Initial contract |
