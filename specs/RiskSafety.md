# Risk & Safety Register
**Project:** ML Pipeline Sample  
**Version:** 1.0  
**Date:** 2026-03-08  
**Status:** Draft

---

## 1. Purpose

Identifies, rates, and mitigates risks associated with the ML pipeline's development, deployment, and operation.

## 2. Risk Register

| ID | Risk | Likelihood | Impact | Severity | Mitigation | Owner |
|----|------|-----------|--------|----------|-----------|-------|
| R-01 | Data schema changes break pipeline silently | Medium | High | 🔴 High | Data contract validator in CI (hard gate) | Data Engineer |
| R-02 | Model accuracy degrades after data refresh | Medium | High | 🔴 High | Eval gate blocks merge if below threshold | ML Engineer |
| R-03 | Sensitive PII in training data | Low | Critical | 🔴 High | Data spec prohibits PII; reviewer checklist item | Data Owner |
| R-04 | CI flakiness gives false green | Low | High | 🟡 Medium | Monitor CI pass rate; fix flaky tests immediately | Engineer on-call |
| R-05 | Threshold misconfiguration allows regressions | Low | High | 🟡 Medium | Thresholds in version-controlled YAML; reviewed in PR | ML Lead |
| R-06 | Stale eval dataset causes blind spots | Medium | Medium | 🟡 Medium | Dataset refresh cadence defined in EvalPlan | ML Engineer |
| R-07 | Credentials committed to repo | Low | Critical | 🔴 High | `.gitignore` + GitHub secret scanning enabled | All |
| R-08 | Spec documents not updated with code | Medium | Medium | 🟡 Medium | DoD requires spec review as release criterion | Reviewer |

## 3. Severity Matrix

```
           Low Impact   Med Impact   High Impact   Critical Impact
Low Like.    🟢 Low      🟢 Low       🟡 Medium     🔴 High
Med Like.    🟢 Low      🟡 Medium    🔴 High       🔴 High
High Like.   🟡 Medium   🔴 High      🔴 High       🔴 High
```

## 4. Safety Controls

| Control | Description | Enforced By |
|---------|-------------|-------------|
| Data contract validation | Blocks pipeline on schema/value violations | CI (`make data-check`) |
| Eval gate | Blocks merge if accuracy/F1 below threshold | CI (`make eval-gate`) |
| Branch protection | Requires CI green + reviewer approval to merge to `main` | GitHub branch rules |
| Secret scanning | Detects accidentally committed credentials | GitHub Advanced Security |
| Artifact retention | Reports kept 30 days for audit trail | GitHub Actions |

## 5. Residual Risk Acceptance

Risks rated 🟡 Medium are accepted pending the mitigations above.  
Risks rated 🔴 High require active mitigation before the first production release.  
No 🔴 High residual risks are acceptable at release.

## 6. Review Cadence

Risk register reviewed: **every sprint** or after any production incident.

## 7. Versioning

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-08 | Initial risk register |
