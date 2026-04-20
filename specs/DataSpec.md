# DataSpec — AI Spec Pack

**Version:** 1.0.0  
**Last updated:** 2026-04-19

---

## 1. Overview

This document specifies the data requirements for training, validation, evaluation, and production inference.

---

## 2. Datasets

| Name | Split | Format | Location | Size |
|---|---|---|---|---|
| `golden_set` | eval | JSONL | `data/golden_set.jsonl` | 30 examples |
| `sample_train` | train | CSV | `data/sample_train.csv` | 50 rows |
| `sample_val` | val | CSV | `data/sample_val.csv` | 20 rows |

---

## 3. Feature Specification

### 3.1 Input Features

| Feature | Type | Range / Values | Nullable | Description |
|---|---|---|---|---|
| `text` | string | 1–4096 chars | No | Raw input text to classify |
| `source` | string | `web`, `api`, `mobile` | Yes | Origin of the request |
| `locale` | string | ISO 639-1+3166 | Yes | User locale (e.g. `en-US`) |
| `user_tier` | string | `free`,`pro`,`enterprise` | Yes | Subscription tier |

### 3.2 Label Specification

| Label | Type | Values | Description |
|---|---|---|---|
| `label` | categorical | `positive`, `negative`, `neutral` | Ground-truth sentiment class |
| `confidence_gt` | float | [0.0, 1.0] | Human annotator agreement score |

---

## 4. Preprocessing Pipeline

1. **Normalise** — lowercase, strip leading/trailing whitespace.
2. **Truncate** — hard-cap at 512 tokens (model limit); log truncation events.
3. **Filter** — drop rows where `text` is null, empty, or whitespace-only after normalisation.
4. **Encode** — tokenise using the project tokeniser (`src/tokeniser.py`).

---

## 5. Data Quality Requirements

| Check | Rule | Severity |
|---|---|---|
| No empty `text` | All rows must have `len(text.strip()) > 0` | FAIL |
| No duplicates | `(text, label)` pairs must be unique | FAIL |
| Label coverage | All three labels must appear at least once | FAIL |
| Class imbalance | No single class > 70 % of total | WARN |
| Distribution shift | KS p-value > 0.05 vs reference distribution | WARN |
| Source dominance | No single `source` value > 80 % | WARN |

---

## 6. Versioning

Data assets are versioned with the pattern `YYYY-MM-DD-vN` (e.g. `2026-04-19-v1`). Breaking schema changes increment the major version in `DataContract.md`.
