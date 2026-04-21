# Incident Playbook — AI Spec Pack

**Version:** 1.0.0  
**Last updated:** 2026-04-21  
**On-call rotation:** ML Lead → Infra Lead → Data Eng

---

## Severity Levels

| Level | Description | Response Time | Example |
|---|---|---|---|
| P0 | Full service outage | < 15 min | All requests failing |
| P1 | Partial outage / SLO breach | < 30 min | p95 > 1 500 ms |
| P2 | Degraded quality | < 2 hours | Coverage < 80% |
| P3 | Warning / investigation needed | Next business day | Drift detected |

---

---

# Incident Type 1 — High Latency / Timeout Spike

**Trigger:** `CriticalLatencyP95` alert — p95 > 1 500 ms for 5+ minutes  
**Severity:** P1

## Detection
- Alert fires via PagerDuty
- `timeout_rate` > 0.5% visible in dashboard
- Users report slow responses

## Immediate Response (0–15 min)
1. **Acknowledge** the alert in PagerDuty
2. Check current traffic volume — is it a load spike?
   ```bash
   # Check request rate
   curl https://your-metrics-endpoint/rps
   ```
3. Check model replica health — are all replicas running?
4. If load spike → **scale up replicas** (max 10 per resource envelope)
5. If not load spike → **trigger fallback to lite model**:
   - Set `FALLBACK_MODE=lite` in environment config
   - Redeploy service

## Investigation (15–60 min)
- Check recent deployments — did a new model ship in last 2 hours?
- Profile inference: feature extraction vs model forward pass
- Check GPU/CPU utilization — resource saturation?

## Resolution
- If new model caused it → **rollback**:
  ```bash
  git revert HEAD --no-edit && git push origin main
  ```
- If infrastructure → scale or migrate replicas
- If persistent → escalate to Infra Lead

## Post-Incident
- [ ] Write incident report within 24 h
- [ ] Add regression test to `tests/test_slo_gate.py`
- [ ] Update alert threshold if needed

---

---

# Incident Type 2 — Model Quality Degradation

**Trigger:** Live Macro-F1 drops > 5pp vs baseline OR coverage < 70%  
**Severity:** P2 (escalates to P1 if coverage < 50%)

## Detection
- `LowCoverage` alert fires
- Unusual label distribution in monitoring dashboard (e.g. 90% `uncertain`)
- User feedback / downstream system anomaly

## Immediate Response (0–30 min)
1. **Verify** — check `reports/metrics.json` vs `configs/thresholds.yaml`
   ```bash
   make eval-gate
   ```
2. Is the golden set still valid? Re-run eval:
   ```bash
   python src/eval.py --golden data/golden_set.jsonl --out reports/metrics.json
   ```
3. If eval gate fails → **halt new traffic routing** (stay on old model)
4. Check if data contract has changed — run:
   ```bash
   make data-check
   ```

## Investigation (30 min – 2 h)
- Compare current prediction distribution vs baseline
- Check if input data has shifted (new source, new format)
- Review recent data pipeline changes
- Check if model artifact was corrupted during last deploy

## Resolution
| Root Cause | Action |
|---|---|
| Data drift | Retrain with recent data + re-evaluate |
| Corrupted model artifact | Rollback to previous model version |
| Label schema change | Update `DataContract.md` + retrain |
| Golden set stale | Refresh golden set + re-evaluate |

## Post-Incident
- [ ] Root cause documented
- [ ] Monitoring check added for the specific failure mode
- [ ] Dataset Card updated if data changed

---

---

# Incident Type 3 — Service Outage (Full Failure)

**Trigger:** `LowAvailability` alert — availability < 99.5% over rolling 1 hour  
**Severity:** P0

## Detection
- All requests returning HTTP 503
- `status=error` rate = 100%
- Health check endpoint unreachable

## Immediate Response (0–15 min)
1. **Declare P0** — notify ML Lead + Infra Lead immediately
2. Activate **rule-based fallback** (always available, no ML dependency):
   - Set `FALLBACK_MODE=rules` in environment config
   - This returns keyword-based labels with `status=fallback`
3. Verify fallback is serving traffic
4. Check service logs for crash cause:
   ```bash
   # Last 100 error lines
   journalctl -u ml-service --since "10 min ago" | grep ERROR
   ```

## Investigation (15–45 min)
- Container crash? → check OOM killer, restart policy
- Dependency failure? → check model artifact storage (S3/GCS)
- Network issue? → check load balancer and DNS
- Deployment gone wrong? → check last CI run

## Resolution
```bash
# Option A: Rollback last deployment
git revert HEAD --no-edit
git push origin main

# Option B: Force restart service
kubectl rollout restart deployment/ml-inference

# Option C: Scale from zero if replicas = 0
kubectl scale deployment/ml-inference --replicas=2
```

## Communication
- **< 15 min:** Internal Slack alert to #incidents
- **< 30 min:** Status page updated: "Investigating degraded service"
- **< 60 min:** Status page updated with ETA
- **On resolution:** Status page: "Resolved — root cause under investigation"

## Post-Incident
- [ ] Full incident report within 48 h
- [ ] Blameless post-mortem scheduled
- [ ] Error budget impact calculated
- [ ] Runbook updated with new findings
- [ ] Monitoring gap identified and filled

---

## Incident Report Template

```markdown
## Incident Report — [Date] — [Title]

**Severity:** P0 / P1 / P2  
**Duration:** HH:MM  
**Impact:** X% of requests affected  

### Timeline
- HH:MM — Alert fired
- HH:MM — On-call acknowledged
- HH:MM — Mitigation applied
- HH:MM — Service restored

### Root Cause
[One paragraph explanation]

### What Went Well
- 

### What Went Wrong
- 

### Action Items
| Action | Owner | Due |
|---|---|---|
| | | |
```
