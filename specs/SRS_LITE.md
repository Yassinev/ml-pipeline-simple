# SRS_LITE — AI Spec Pack System

**Version:** 1.0.0  
**Status:** Draft  
**Last updated:** 2026-04-19

---

## 1. Purpose

This document defines the functional and non-functional requirements for an AI classification/inference system. It establishes the contract between product, data, modelling, and operations teams.

---

## 2. Input / Output Schemas

### 2.1 Input Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "InferenceRequest",
  "type": "object",
  "required": ["request_id", "text", "timestamp"],
  "properties": {
    "request_id": { "type": "string", "format": "uuid" },
    "text":       { "type": "string", "minLength": 1, "maxLength": 4096 },
    "timestamp":  { "type": "string", "format": "date-time" },
    "metadata": {
      "type": "object",
      "properties": {
        "source":   { "type": "string" },
        "locale":   { "type": "string", "pattern": "^[a-z]{2}-[A-Z]{2}$" },
        "user_tier":{ "type": "string", "enum": ["free","pro","enterprise"] }
      }
    }
  },
  "additionalProperties": false
}
```

### 2.2 Output Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "InferenceResponse",
  "type": "object",
  "required": ["request_id", "label", "confidence", "latency_ms", "status"],
  "properties": {
    "request_id": { "type": "string", "format": "uuid" },
    "label":      { "type": "string", "enum": ["positive","negative","neutral","uncertain"] },
    "confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
    "latency_ms": { "type": "integer", "minimum": 0 },
    "status":     { "type": "string", "enum": ["ok","fallback","timeout","error"] },
    "fallback_reason": { "type": "string" }
  },
  "additionalProperties": false
}
```

---

## 3. Degradation Rules

### 3.1 Timeout Handling

| Stage | Timeout | Behaviour |
|---|---|---|
| Feature extraction | 500 ms | Abort request; return `status=timeout` with `label=uncertain` |
| Model inference | 1 500 ms | Abort; return `status=timeout` with `label=uncertain` |
| End-to-end (wall clock) | 2 500 ms | Return `status=timeout`; log SLO breach |

### 3.2 Uncertainty Zone

- If `confidence < 0.55`: set `label=uncertain`, `status=ok`.
- Downstream consumers **must not** act on `label=uncertain` without human review.
- Uncertain predictions are excluded from accuracy KPIs but counted in coverage KPIs.

### 3.3 Fallback Hierarchy

1. **Primary model** — full transformer inference.
2. **Lite model** — distilled model (triggers if primary latency p95 > 1 200 ms over 60 s window).
3. **Rule-based baseline** — keyword heuristic (triggers if lite model error rate > 5 %).
4. **Reject** — return `status=error`, HTTP 503, after all fallbacks exhausted.

---

## 4. Non-Functional Requirements (NFRs)

### 4.1 Latency

| Percentile | Target | Hard Limit |
|---|---|---|
| p50 | ≤ 300 ms | — |
| p95 | ≤ 900 ms | 1 500 ms |
| p99 | ≤ 1 800 ms | 2 500 ms |

### 4.2 Availability

- **Target SLO:** 99.5 % uptime measured monthly (rolling 30 days).
- Planned maintenance windows excluded (max 4 h/month, announced 48 h in advance).
- Degraded mode (fallback active) counts as **available**.

### 4.3 Cost

| Budget item | Limit |
|---|---|
| Inference cost per 1 000 requests | ≤ $0.10 USD |
| Monthly GPU/API spend | ≤ $500 USD |
| Cost per labelled sample (annotation) | ≤ $0.30 USD |

---

## 5. Glossary

| Term | Definition |
|---|---|
| Uncertainty zone | Confidence band [0, 0.55) where prediction is unreliable |
| Fallback | Secondary system activated on primary failure |
| SLO breach | Single request exceeding the hard latency limit |
