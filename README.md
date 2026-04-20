# AI Spec Pack

A fully-specified, CI-driven skeleton for an AI classification system.
Covers HW1–HW4 (repo structure, requirements, data pipeline, model spec + eval gate).

## Quick start

```bash
pip install -r requirements.txt
make test        # schema + unit tests
make data-check  # 13 automated data checks
make eval-gate   # golden-set eval + threshold gate + regression check
```

## Repository layout

```
.
├── .github/workflows/ci.yml   # GitHub Actions — runs all three make targets
├── configs/
│   └── thresholds.yaml        # Eval-gate pass/fail thresholds
├── data/
│   ├── golden_set.jsonl       # 38-example balanced golden set (HW4)
│   ├── sample_train.csv       # 50-row training sample
│   └── sample_val.csv         # 20-row validation sample
├── reports/
│   ├── metrics.json           # Latest eval-gate results (written by make eval-gate)
│   └── metrics_prev.json      # Previous run — used for regression detection
├── specs/
│   ├── SRS_LITE.md            # Input/output schemas, degradation rules, NFRs (HW2)
│   ├── Acceptance_Criteria_Table.md  # 15-scenario AC table (HW2)
│   ├── DataSpec.md            # Feature spec + quality requirements (HW3)
│   ├── DataContract.md        # Breaking/non-breaking change rules (HW3)
│   ├── Dataset_Card.md        # Source, purpose, limits, versioning (HW3)
│   ├── ModelSpec.md           # Baseline, limits, resource envelope, update policy (HW4)
│   └── EvalPlan.md            # Metrics, 6 slices, gates, regression rule (HW4)
├── src/
│   ├── schemas.py             # Request/response schema validators
│   ├── model.py               # Mock classifier (replace with real model)
│   └── eval.py                # Evaluation runner → reports/metrics.json
├── tests/
│   ├── test_schemas.py        # Unit tests (make test)
│   ├── test_data_checks.py    # 13 data checks — 3 syntactic, 4 structural, 3 statistical + golden (make data-check)
│   └── test_eval_gate.py      # 17 gate tests — G1–G5 + regression (make eval-gate)
├── Makefile
└── requirements.txt
```

## CI gates

| Make target | Tests | What it checks |
|---|---|---|
| `make test` | 22 | Schema validation, model contract, AC edge cases |
| `make data-check` | 13 | Syntactic / structural / statistical data quality |
| `make eval-gate` | 17 | Macro-F1, accuracy, coverage, 6 slices, regression |

## Replacing the mock model

`src/model.py` contains a keyword-heuristic stub. To plug in a real model:

1. Replace `predict()` with your inference call.
2. Run `make eval-gate` to regenerate `reports/metrics.json`.
3. Copy it to `reports/metrics_prev.json` to establish the new baseline.
4. Raise thresholds in `configs/thresholds.yaml` to production targets.

## Spec documents at a glance

| Doc | Key content |
|---|---|
| `SRS_LITE.md` | JSON schemas, timeout/fallback chain, latency/availability/cost NFRs |
| `Acceptance_Criteria_Table.md` | 15 scenarios (normal/edge/boundary/negative) with metrics, thresholds, measurement methods |
| `DataSpec.md` | Feature types, preprocessing pipeline, quality rules |
| `DataContract.md` | SLA, breaking vs non-breaking change policy |
| `Dataset_Card.md` | Provenance, intended use, non-use, known limitations |
| `ModelSpec.md` | Baseline comparison, applicability limits, resource envelope, update policy |
| `EvalPlan.md` | 6 evaluation metrics, 6 slices, 5 gates (G1–G5), regression rule |
