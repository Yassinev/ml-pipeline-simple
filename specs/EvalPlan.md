# Evaluation Plan
**Project:** ML Pipeline Sample  
**Version:** 1.0  
**Date:** 2026-03-08  
**Status:** Draft

---

## 1. Purpose

This document defines how model quality is measured, what thresholds constitute a passing release, and how evaluation is automated in CI.

## 2. Evaluation Philosophy

Every merge to `main` MUST pass a quantitative eval gate. Metrics are compared against thresholds defined in `configs/thresholds.yaml`. Subjective reviews supplement but do NOT replace automated gates.

## 3. Metrics & Thresholds

| Metric | Description | Threshold | Criticality |
|--------|-------------|-----------|-------------|
| `accuracy` | Fraction of correct predictions | ≥ 0.80 | Hard gate (CI fails) |
| `f1_score` | Harmonic mean of precision & recall | ≥ 0.75 | Hard gate (CI fails) |
| `precision` | TP / (TP + FP) | ≥ 0.70 | Soft warning |
| `recall` | TP / (TP + FN) | ≥ 0.70 | Soft warning |
| `latency_p95_ms` | 95th percentile inference latency | ≤ 500 ms | Soft warning |

Thresholds are read from `configs/thresholds.yaml` — change the file, not the code.

## 4. Evaluation Dataset

| Property | Value |
|----------|-------|
| Source | `data/sample_requests.jsonl` |
| Size | ≥ 50 labelled records |
| Split | 80% train / 20% eval |
| Refresh cadence | Each sprint |

## 5. Evaluation Procedure

### 5.1 Automated (CI Gate)
```
make eval-gate
```
Steps executed:
1. Load `reports/metrics_example.json`
2. Load thresholds from `configs/thresholds.yaml`
3. Compare each metric to its threshold
4. Exit `0` if all hard-gate metrics pass; exit `1` otherwise
5. Write `reports/eval_report.json` with pass/fail details

### 5.2 Manual Review (Pre-Release)
- Reviewer inspects `reports/eval_report.json`
- Reviewer checks for metric cliff drops (> 5% vs previous release)
- Sign-off required in PR description

## 6. Reporting

All eval outputs are uploaded as CI artifacts:
- `reports/eval_report.json` — machine-readable pass/fail per metric
- `reports/metrics_example.json` — raw computed metrics

Artifacts are retained for **30 days** in GitHub Actions.

## 7. Failure Response

| Scenario | Action |
|----------|--------|
| Hard gate metric below threshold | CI fails, PR blocked |
| Soft warning metric below threshold | CI passes, comment added to PR |
| Eval script crashes | CI fails, engineer investigates |
| Dataset missing | CI fails, data team notified |

## 8. Versioning

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-08 | Initial eval plan |
