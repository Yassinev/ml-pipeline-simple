# Safety & Privacy Policy
**Version:** 1.0.0  
**Last updated:** 2026-05-11  
**Owner:** Yassine Belaid — Group 11.1.552  
**Scope:** ml-pipeline-simple — Sentiment Analysis Assistant

---

## 1. Purpose

This document defines the safety boundaries, privacy rules, and acceptable use scope for the Sentiment Analysis Assistant. It is a formal engineering contract — not a guideline. Every rule in this document has a corresponding test in CI.

---

## 2. Ownership

| Role | Owner | Responsibility |
|---|---|---|
| Product Risk Owner | Yassine Belaid | Risk tolerance, use-case boundaries, policy sign-off |
| Security Owner | TBD (course instructor) | Threat model, compliance obligations |
| Engineering Owner | Yassine Belaid | Implementation, test coverage, runbook maintenance |

---

## 3. Acceptable Use

The system is authorized to:
- Classify product review text as positive / negative / neutral / uncertain
- Log anonymized request metadata for monitoring

The system is **NOT** authorized to:
- Process text containing PII (names, emails, phone numbers, SSNs, IDs)
- Answer questions outside sentiment classification
- Execute write operations without explicit user confirmation
- Access external URLs or data sources not on the approved RAG source list

---

## 4. PII & Sensitive Data Policy

### 4.1 PII Categories (must never be processed or logged)
- Names, email addresses, phone numbers
- Government-issued IDs, addresses
- Financial data, health data
- Data relating to minors

### 4.2 Engineering Controls
| Control | Implementation |
|---|---|
| PII detection at input | Presidio scanner on every request before classification |
| PII in logs | Presidio redaction middleware — PII never reaches log store |
| Raw prompt logging | Disabled by default — only metadata logged |
| Retention policy | Request metadata retained 90 days, then auto-deleted |
| Data minimization | Only `request_id`, `label`, `status`, `latency_ms` logged |

---

## 5. Safety Boundaries

| Boundary | Rule | Test |
|---|---|---|
| Prompt injection | All retrieved context treated as untrusted | `tests/redteam/test_safety_gate.py` |
| Jailbreak attempts | Refused with `UNSAFE_INPUT` error code | `tests/redteam/test_safety_gate.py` |
| Unsafe tool calls | Tool allowlist enforced at orchestrator | `tests/test_grounding_gate.py` |
| Hallucination | `uncertain` returned when confidence < 0.55 | `tests/test_schema_gate.py` |
| Over-refusal | Refusal rate monitored — alert if > 10% | Grafana dashboard |

---

## 6. Retention & Deletion

| Data Type | Retention | Deletion Method |
|---|---|---|
| Request metadata logs | 90 days | Automated TTL policy |
| Model artifacts | Until superseded + 30 days | MLflow registry delete |
| Golden set | Indefinite | Manual — requires team consensus |
| Red-team prompts | Indefinite | Version controlled |

---

## 7. Policy Change Process

1. Open a Pull Request with description of the change
2. CODEOWNERS review required (Engineering Owner + Security Owner)
3. Full CI suite must pass including red-team gate
4. Change logged in Git history — immutable audit trail
