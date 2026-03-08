# Monitoring Playbook
**Project:** ML Pipeline Sample  
**Version:** 1.0  
**Date:** 2026-03-08  
**Status:** Draft

---

## 1. Purpose

This playbook defines what to monitor, how to detect anomalies, and the runbook for each alert type.

## 2. Monitoring Dimensions

| Dimension | What to Watch | Tool |
|-----------|--------------|------|
| Data Quality | Schema violations, null rates, score distribution | `make data-check` + CI |
| Model Performance | Accuracy, F1 drift vs baseline | `make eval-gate` + CI |
| Pipeline Health | CI pass rate, workflow duration | GitHub Actions dashboard |
| Latency | P95 inference time | Metrics in `reports/` |

## 3. Key Signals & Thresholds

| Signal | Warning | Critical |
|--------|---------|----------|
| Accuracy drop vs last release | > 3% | > 5% |
| F1 drop vs last release | > 3% | > 5% |
| Null rate in input data | > 1% | > 5% |
| CI failure rate (7-day rolling) | > 5% | > 15% |
| Eval gate duration | > 2 min | > 5 min |

## 4. Alert Runbooks

### 4.1 Accuracy Below Threshold
1. Check `reports/eval_report.json` for which split failed.
2. Compare against previous release metrics.
3. Inspect recent data changes (`data/` git diff).
4. If data drift suspected → re-run `make data-check`.
5. If model regression → revert last model change and re-evaluate.
6. Escalate to ML lead if not resolved within 2 hours.

### 4.2 Data Contract Violation
1. Run `make data-check` locally to reproduce.
2. Identify which DQ rule failed (see `specs/DataSpec.md`).
3. Trace back to the data producer.
4. Fix upstream or add data repair step.
5. Re-run pipeline after fix; confirm CI green.

### 4.3 CI Pipeline Failure (non-gate)
1. Check GitHub Actions logs for step that failed.
2. If environment issue (missing package) → update `requirements.txt`.
3. If flaky test → investigate and fix; do not re-run to paper over it.
4. Assign to owning engineer within 30 minutes.

## 5. Dashboards & Reports

| Artifact | Location | Refresh |
|----------|----------|---------|
| Eval report | `reports/eval_report.json` | Per CI run |
| CI status | GitHub Actions tab | Real-time |
| Metric history | Git history of `reports/` | Per merge |

## 6. On-Call Responsibilities

- **Primary:** ML engineer who authored the last merged PR
- **Escalation:** ML lead → Platform team
- **Response SLA:** Acknowledge within 30 min; resolve within 4 hours

## 7. Versioning

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-08 | Initial playbook |
