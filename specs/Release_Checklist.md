# Release Checklist

**Version:** 1.0.0  
**Last updated:** 2026-04-21  
**Owner:** ML Lead

---

## Pre-Release (before any deployment)

### Code & Tests
- [ ] All PRs merged to `main`
- [ ] `make test` passes — 0 failures
- [ ] `make data-check` passes — 0 contract violations
- [ ] `make eval-gate` passes — all gates G1–G5 green
- [ ] `make slo-gate` passes — SLO thresholds met
- [ ] No open P0/P1 bugs on the milestone

### Data & Model
- [ ] Golden set reviewed — no stale examples
- [ ] `reports/metrics.json` generated from latest golden set
- [ ] Macro-F1 ≥ 0.85 confirmed
- [ ] No regression vs previous release (Δ Macro-F1 ≥ −0.03)
- [ ] Model artifact size ≤ 500 MB
- [ ] Model card updated in `specs/ModelSpec.md`

### Documentation
- [ ] `specs/SRS_LITE.md` reflects any schema changes
- [ ] `CHANGELOG.md` updated with version + date
- [ ] `specs/DataContract.md` version bumped if breaking change
- [ ] Incident playbook reviewed — `specs/Incident_Playbook.md`

### Infrastructure
- [ ] Staging environment tested with production-like traffic
- [ ] Rollback procedure verified (see `specs/Rollout_Plan.md`)
- [ ] Monitoring dashboards updated — `specs/Monitoring_Spec.md`
- [ ] Alert thresholds confirmed in `configs/alert_thresholds.yaml`

---

## Deployment

### Canary Phase (0 → 10% traffic)
- [ ] Deploy canary version to 10% of traffic
- [ ] Monitor for 30 minutes — error rate < 1%
- [ ] p95 latency ≤ 900 ms on canary slice
- [ ] No SLO breach alerts triggered

### Ramp Phase (10 → 50%)
- [ ] Promote to 50% traffic
- [ ] Monitor for 1 hour
- [ ] Macro-F1 on live shadow labels within 3pp of golden set
- [ ] No increase in `status=error` or `status=timeout` rates

### Full Rollout (50 → 100%)
- [ ] Promote to 100% traffic
- [ ] Monitor for 2 hours
- [ ] Confirm SLO dashboard green
- [ ] Send release notification to stakeholders

---

## Post-Release

- [ ] `reports/metrics_prev.json` updated to current release metrics
- [ ] Canary/shadow logs archived
- [ ] Retrospective scheduled (within 48 h)
- [ ] Next release milestone created

---

## Rollback Triggers (automatic or manual)

| Condition | Action |
|---|---|
| Error rate > 2% for 5 min | Automatic rollback to previous version |
| p95 latency > 1 500 ms for 5 min | Automatic rollback |
| Macro-F1 drops > 5pp vs baseline | Manual rollback — ML Lead decision |
| Any P0 incident | Immediate rollback + incident playbook |
