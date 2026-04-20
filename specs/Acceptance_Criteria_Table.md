# Acceptance Criteria Table

**System:** AI Spec Pack Inference Service  
**Version:** 1.0.0  
**Last updated:** 2026-04-19

---

## Legend

| Column | Meaning |
|---|---|
| ID | Unique scenario identifier |
| Category | normal / edge / boundary / negative |
| Scenario | Human-readable description |
| Metric | What is measured |
| Threshold | Pass/fail value |
| Tolerance | Allowed variance |
| Measurement Method | How it is measured |
| Action on Fail | Who does what |

---

## Acceptance Criteria

| ID | Category | Scenario | Metric | Threshold | Tolerance | Measurement Method | Action on Fail |
|---|---|---|---|---|---|---|---|
| AC-01 | normal | Standard positive text produces `label=positive` with high confidence | Accuracy on golden set positives | ≥ 0.90 F1 | ±0.02 | Run `make eval-gate`; compare `reports/metrics.json` to `configs/thresholds.yaml` | Block merge; ML team investigates model regression |
| AC-02 | normal | Standard negative text produces `label=negative` | Accuracy on golden set negatives | ≥ 0.88 F1 | ±0.02 | Same eval gate | Block merge; retrain or rollback |
| AC-03 | normal | End-to-end latency within SLO under typical load (10 req/s) | p95 latency | ≤ 900 ms | +50 ms | Load test in CI using locust or k6 script | Block deploy; infra team profiles bottleneck |
| AC-04 | edge | Empty string input returns validation error | HTTP status code | 422 | none | Integration test `tests/test_api.py::test_empty_input` | Fix input validation layer |
| AC-05 | edge | Input at exact max length (4 096 chars) is processed without truncation error | status field in response | `ok` or `uncertain` (not `error`) | none | Unit test with 4096-char fixture | Fix tokenizer truncation logic |
| AC-06 | edge | Low-confidence prediction (confidence < 0.55) returns `label=uncertain` | label value | `uncertain` | none | Unit test `tests/test_model.py::test_uncertainty_zone` | Fix confidence thresholding logic |
| AC-07 | boundary | Confidence = 0.55 exactly classifies as a definite label (not uncertain) | label value | not `uncertain` | none | Unit test with mocked confidence=0.55 | Fix off-by-one in threshold comparison |
| AC-08 | boundary | Request at exactly p95 latency limit (900 ms) is counted as passing SLO | SLO compliance rate | 100 % for on-threshold requests | none | Replay golden set with simulated 900 ms responses | Fix SLO counter logic |
| AC-09 | negative | Malformed JSON body returns 400 and does not crash service | HTTP status + service uptime | 400; service stays up | none | Integration test with invalid JSON payload | Fix error handling middleware |
| AC-10 | negative | Missing required field `text` returns 422 | HTTP status | 422 | none | Integration test `tests/test_api.py::test_missing_text` | Fix schema validation |
| AC-11 | negative | Inference timeout (>2 500 ms) returns `status=timeout`, not a 500 | status field | `timeout` | none | Unit test with mocked slow model | Fix timeout handling and fallback chain |
| AC-12 | edge | Input containing only whitespace/newlines is rejected | HTTP status | 422 | none | Unit test with `"   \n"` fixture | Add whitespace normalisation to validator |
| AC-13 | normal | Overall macro-F1 on full golden set meets gate | Macro-F1 | ≥ 0.85 | ±0.02 | `make eval-gate` in CI | Block merge; trigger retraining pipeline |
| AC-14 | negative | Injected SQL/prompt in text field does not alter label logic | label is data-driven | deterministic based on semantic content | none | Adversarial test set in `tests/test_adversarial.py` | Security review + fix |
| AC-15 | boundary | Dataset with zero samples of one class does not crash data checks | pytest exit code | 0 (handled gracefully) | none | `make data-check` with synthetic empty-class fixture | Fix imbalance check to warn, not raise, on zero count |
