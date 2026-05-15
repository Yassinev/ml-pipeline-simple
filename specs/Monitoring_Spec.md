# Monitoring Spec — AI Spec Pack

**Version:** 1.0.0  
**Last updated:** 2026-04-21

---

## 1. Monitoring Layers

| Layer | What | Tool |
|---|---|---|
| Infrastructure | CPU, RAM, disk, replicas | Prometheus + Grafana |
| Application | Latency, error rate, throughput | Prometheus + Grafana |
| ML Quality | Prediction distribution, coverage, drift | Custom logger → metrics.json |
| Data | Schema violations, missing fields | CI data-check + runtime validator |

---

## 2. Key Metrics

### 2.1 Latency
| Metric | Description | Unit |
|---|---|---|
| `inference_latency_p50` | Median end-to-end latency | ms |
| `inference_latency_p95` | 95th percentile latency | ms |
| `inference_latency_p99` | 99th percentile latency | ms |

### 2.2 Reliability
| Metric | Description | Unit |
|---|---|---|
| `error_rate` | % requests returning `status=error` | % |
| `timeout_rate` | % requests returning `status=timeout` | % |
| `availability` | % time service is reachable | % |

### 2.3 ML Quality
| Metric | Description | Unit |
|---|---|---|
| `coverage` | % predictions not `uncertain` | % |
| `label_distribution_positive` | % predictions = positive | % |
| `label_distribution_negative` | % predictions = negative | % |
| `label_distribution_neutral` | % predictions = neutral | % |
| `confidence_mean` | Mean confidence score | float |
| `prediction_drift` | KS distance vs baseline distribution | float |

---

## 3. Alert Thresholds

Defined in `configs/alert_thresholds.yaml` and enforced in CI via `make slo-gate`.

| Alert Name | Condition | Severity | Action |
|---|---|---|---|
| `HighLatencyP95` | p95 > 900 ms for 5 min | WARNING | Notify on-call |
| `CriticalLatencyP95` | p95 > 1 500 ms for 5 min | CRITICAL | Auto-rollback |
| `HighErrorRate` | error_rate > 1% for 5 min | WARNING | Notify on-call |
| `CriticalErrorRate` | error_rate > 2% for 5 min | CRITICAL | Auto-rollback |
| `LowCoverage` | coverage < 0.80 for 10 min | WARNING | Notify ML team |
| `LowAvailability` | availability < 99.5% (rolling 1h) | CRITICAL | Incident P0 |
| `PredictionDrift` | KS distance > 0.15 vs baseline | WARNING | ML team review |
| `TimeoutSpike` | timeout_rate > 0.5% for 5 min | WARNING | Infra review |

---

## 4. SLO Definitions

| SLO | Target | Measurement Window |
|---|---|---|
| Availability | ≥ 99.5% | Rolling 30 days |
| p95 Latency | ≤ 900 ms | Rolling 1 hour |
| Error Rate | < 1% | Rolling 1 hour |
| Coverage | ≥ 80% | Rolling 24 hours |

**Error Budget:** 0.5% downtime per month = ~3.6 hours/month

---

## 5. Dashboards

| Dashboard | Panels |
|---|---|
| **Overview** | Availability, error rate, throughput, p95 latency |
| **ML Quality** | Coverage, label distribution, confidence histogram, drift score |
| **Canary** | Side-by-side: old vs new model on all metrics |
| **SLO Burn Rate** | Error budget remaining, burn rate over 1h/6h/24h |

---

## 6. Log Schema

Every request logged as JSON:
```json
{
  "request_id": "uuid",
  "timestamp": "ISO-8601",
  "label": "positive",
  "confidence": 0.91,
  "latency_ms": 245,
  "status": "ok",
  "model_version": "1.0.0",
  "canary": false
}
```
