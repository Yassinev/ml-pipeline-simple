# Homework PR — ML Pipeline Deliverables

## 1-Page PRD Summary

This ML pipeline provides a production-style framework for shipping AI features safely. The problem: ML teams lack standardized, automated release gates, leading to data quality incidents and silent regressions. The solution: a CI-enforced pipeline that validates data against a schema contract and blocks merges when model metrics fall below defined thresholds. Success is defined as green CI on every PR — meaning data checks pass, eval gates pass (accuracy ≥ 0.80, F1 ≥ 0.75), and all six spec documents are present and filled in.

---

## DoD Artifact List

### Automated (CI-enforced — must be green to merge)

- [x] **A-01** Unit tests pass → `pytest tests/` → CI `test` job
- [x] **A-02** Data contract check passes → `make data-check` → CI `data-check` job
- [x] **A-03** Eval gate passes (accuracy ≥ 0.80, F1 ≥ 0.75) → `make eval-gate` → CI `eval-gate` job
- [x] **A-04** Eval report uploaded as artifact → CI artifact: `eval-report`
- [x] **A-05** All CI steps exit 0 → PR status checks green

### Manual (Reviewer sign-off required)

- [x] **M-01** All 6 spec files present in `/specs`: PRD, SRS, DataSpec, EvalPlan, Monitoring, RiskSafety, DoD
- [x] **M-02** `configs/thresholds.yaml` reviewed — thresholds set intentionally
- [x] **M-03** No PII or credentials committed
- [x] **M-04** `reports/eval_report.json` reviewed — no metric cliffs vs baseline
- [x] **M-05** PR description complete (this document)
- [x] **M-06** Spec docs reflect current scope

---

## Files Changed in This PR

```
specs/
  PRD.md           ← 1-page PRD with goals, metrics, user stories
  SRS.md           ← System requirements with testable FR/NFR
  DataSpec.md      ← Schema, field constraints, data contract rules
  EvalPlan.md      ← Metrics, thresholds, eval procedure
  Monitoring.md    ← Signals, alert runbooks, on-call guide
  RiskSafety.md    ← Risk register with mitigations
  DoD.md           ← Release-ready checklist linked to CI

.github/workflows/
  ci.yml           ← GitHub Actions: test → data-check → eval-gate

src/aispec/
  data_contract.py ← DQ rules validator (exits 1 on violation)
  eval_gate.py     ← Threshold gate (exits 1 if hard metric fails)

tests/
  test_gates.py    ← Unit tests for both gate modules

configs/
  thresholds.yaml  ← accuracy ≥ 0.80, f1_score ≥ 0.75 (configurable)

data/
  sample_requests.jsonl   ← 5 valid sample records

reports/
  metrics_example.json    ← Sample metrics (accuracy=0.87, f1=0.83)
```

---

## CI Link

> *(Paste the URL of your passing GitHub Actions run here after pushing)*  
> Example: `https://github.com/<your-username>/ml-pipeline-sample/actions/runs/<run-id>`

---

## How to Run Locally

```bash
# 1. Clone and install
git clone https://github.com/<your-username>/ml-pipeline-sample
cd ml-pipeline-sample
pip install -r requirements.txt

# 2. Run all gates
make test        # unit tests
make data-check  # data contract validator
make eval-gate   # eval threshold gate

# 3. View report
cat reports/eval_report.json
```
