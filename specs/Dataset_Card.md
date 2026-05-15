# Dataset Card — AI Spec Pack Sample Dataset

**Version:** 1.0.0  
**Last updated:** 2026-04-19

---

## 1. Dataset Summary

A small, curated sentiment-classification dataset used for unit testing, CI validation, and golden-set evaluation of the AI Spec Pack inference system. It is **not** intended as a production training corpus.

---

## 2. Source & Provenance

| Field | Value |
|---|---|
| Origin | Synthetically generated for project bootstrapping |
| Collection method | Human-authored examples covering three sentiment classes |
| Collection period | April 2026 |
| License | MIT (same as repository) |
| PII | None — all texts are artificial |

---

## 3. Purpose & Intended Use

- Smoke-testing the data validation pipeline (`make data-check`).
- Serving as a minimal golden set for `make eval-gate`.
- Providing a reference fixture for unit tests.

---

## 4. Non-Use (Out of Scope)

- **Do not** use as a primary training set for production models.
- **Do not** use to benchmark against external benchmarks without noting its synthetic origin.
- **Do not** treat label distribution as representative of real-world data.

---

## 5. Composition

| Split | File | Rows | Positive | Negative | Neutral |
|---|---|---|---|---|---|
| Train | `data/sample_train.csv` | 50 | 17 | 17 | 16 |
| Val | `data/sample_val.csv` | 20 | 7 | 7 | 6 |
| Golden eval | `data/golden_set.jsonl` | 30 | 10 | 10 | 10 |

Total: 100 examples.

---

## 6. Labelling

- Labels assigned by the dataset author.
- No inter-annotator agreement computed (single annotator, synthetic data).
- `confidence_gt` is set to 1.0 for all synthetic examples.

---

## 7. Known Limitations

- Synthetic texts lack the noise, slang, and ambiguity of real user input.
- Class balance is artificial; real distributions may differ significantly.
- Only English (`en-US`) texts are included.
- No demographic or geographic diversity.

---

## 8. Version History

| Version | Date | Changes |
|---|---|---|
| 1.0.0 | 2026-04-19 | Initial release — 100 synthetic examples |
