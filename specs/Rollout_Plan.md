# Rollout Plan — Canary & Shadow Deployment

**Version:** 1.0.0  
**Last updated:** 2026-04-21

---

## 1. Strategy Overview

We use a **3-phase canary rollout** combined with **shadow mode** evaluation before any traffic is moved.

```
Shadow Mode → Canary 10% → Ramp 50% → Full 100%
```

---

## 2. Shadow Mode (Pre-Canary)

**What it is:** New model runs in parallel with production, receiving all requests but **never returning its predictions to users**. Predictions are logged and compared offline.

**Duration:** 24 hours minimum  
**Traffic:** 100% of production requests (mirrored, no user impact)

### Success Criteria
| Metric | Threshold |
|---|---|
| Shadow Macro-F1 vs prod | Within ±3pp |
| Shadow error rate | < 0.5% |
| Shadow p95 latency | ≤ 1 200 ms |
| Shadow coverage | ≥ 0.80 |

### Failure Action
If any criterion fails → **do not proceed to canary** → investigate + retrain.

---

## 3. Canary Phase — 10% Traffic

**Duration:** 30 minutes minimum  
**Traffic split:** 10% new model / 90% old model

### Monitoring Window
- Check every 5 minutes
- Auto-rollback if error rate > 2% or p95 > 1 500 ms

### Success Criteria
| Metric | Threshold |
|---|---|
| Error rate | < 1% |
| p95 latency | ≤ 900 ms |
| `status=timeout` rate | < 0.5% |
| User-facing label distribution | Within 5pp of baseline |

---

## 4. Ramp Phase — 50% Traffic

**Duration:** 1 hour minimum  
**Traffic split:** 50% new model / 50% old model

### Success Criteria
| Metric | Threshold |
|---|---|
| All canary criteria | Still passing |
| Live shadow F1 proxy | ≥ 0.82 |
| No P0/P1 incidents | 0 incidents |

---

## 5. Full Rollout — 100% Traffic

**Duration:** Monitor for 2 hours post-rollout

### Success Criteria
| Metric | Threshold |
|---|---|
| SLO compliance | ≥ 99.5% |
| p95 latency | ≤ 900 ms |
| Error rate | < 1% |
| Coverage | ≥ 0.80 |

---

## 6. Rollback Procedure

### Automatic Rollback (triggered by monitoring)
1. Alert fires (error rate > 2% or p95 > 1 500 ms for 5 min)
2. Traffic router reverts to 0% new model instantly
3. On-call engineer notified via PagerDuty
4. Incident opened in `specs/Incident_Playbook.md`

### Manual Rollback
```bash
# Revert to previous model version
git revert HEAD --no-edit
git push origin main
# CI re-deploys previous version automatically
```

---

## 7. Traffic Routing Configuration

```yaml
# configs/rollout.yaml
rollout:
  strategy: canary
  stages:
    - name: shadow
      traffic_pct: 0
      shadow: true
      min_duration_hours: 24
    - name: canary
      traffic_pct: 10
      min_duration_minutes: 30
    - name: ramp
      traffic_pct: 50
      min_duration_minutes: 60
    - name: full
      traffic_pct: 100
      min_duration_minutes: 120
  auto_rollback:
    error_rate_threshold: 0.02
    latency_p95_threshold_ms: 1500
    window_minutes: 5
```
