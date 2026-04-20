# EvalPlan — AI Spec Pack

**Version:** 1.0.0  
**Last updated:** 2026-04-19

---

## 1. Evaluation Objectives

1. Verify model meets quality gates before every merge to `main`.
2. Detect performance regressions vs the previous released version.
3. Surface slice-level degradation that aggregate metrics hide.

---

## 2. Metrics

| Metric | Formula | Primary? | Gate |
|---|---|---|---|
| Macro-F1 | Unweighted mean of per-class F1 | ✅ Yes | ≥ 0.85 |
| Accuracy | Correct / Total | No | ≥ 0.82 |
| Precision (macro) | Mean per-class precision | No | ≥ 0.83 |
| Recall (macro) | Mean per-class recall | No | ≥ 0.83 |
| Coverage | 1 − (uncertain / total) | No | ≥ 0.80 |
| Latency p95 | 95th percentile wall time | ✅ Yes | ≤ 900 ms |

---

## 3. Evaluation Slices

At least 6 slices must be reported individually in `reports/metrics.json`:

| Slice ID | Dimension | Definition |
|---|---|---|
| S1 | Class: positive | All examples with `label=positive` |
| S2 | Class: negative | All examples with `label=negative` |
| S3 | Class: neutral | All examples with `label=neutral` |
| S4 | Short text | `len(text) ≤ 50` chars |
| S5 | Long text | `len(text) > 200` chars |
| S6 | Low annotator confidence | `confidence_gt < 0.80` |

Each slice must have Macro-F1 ≥ 0.75 (soft warning below 0.80; hard fail below 0.75).

---

## 4. Thresholds & Gates

All gates are enforced in `tests/test_eval_gate.py` by comparing `reports/metrics.json` to `configs/thresholds.yaml`.

| Gate | Metric | Hard Fail |
|---|---|---|
| G1 | Overall Macro-F1 | < 0.85 |
| G2 | Overall Accuracy | < 0.82 |
| G3 | Coverage | < 0.80 |
| G4 | Any slice Macro-F1 | < 0.75 |
| G5 | Regression vs prev | Δ Macro-F1 < −0.03 |

---

## 5. Regression Rule

A regression is declared when **any** of the following conditions hold:

- Overall Macro-F1 decreases by more than **0.03** vs the last passing CI run.
- Any slice F1 decreases by more than **0.05** vs the last passing CI run.
- Coverage drops by more than **0.05**.

The previous metrics are stored in `reports/metrics_prev.json` and compared automatically in `tests/test_eval_gate.py`.

---

## 6. Golden Set

- File: `data/golden_set.jsonl`
- Size: 30 examples (10 per class — balanced by design)
- Refresh policy: Reviewed quarterly; examples may be added but never removed without team consensus.
- Requirement: Every PR must run the full golden set; partial subsets not accepted.

---

## 7. Reporting

`make eval-gate` writes results to `reports/metrics.json`:

```json
{
  "overall": {
    "macro_f1": 0.87,
    "accuracy": 0.87,
    "coverage": 0.93
  },
  "slices": {
    "positive": { "f1": 0.90 },
    "negative": { "f1": 0.86 },
    "neutral":  { "f1": 0.85 },
    "short_text":  { "f1": 0.82 },
    "long_text":   { "f1": 0.88 },
    "low_conf_gt": { "f1": 0.78 }
  }
}
```
