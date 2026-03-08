# Definition of Done (DoD)
**Project:** ML Pipeline Sample  
**Version:** 1.0  
**Date:** 2026-03-08

---

## Purpose

A release to `main` is **release-ready** when every item below is checked. This DoD is enforced by CI status checks — a PR cannot merge unless the automated items are green.

---

## Release-Ready Checklist

### ✅ Automated (Enforced by CI — must be green to merge)

| # | Criterion | CI Check | How to Verify |
|---|-----------|----------|---------------|
| A-01 | Unit tests pass | `pytest tests/` | GitHub Actions → `test` step |
| A-02 | Data contract check passes | `make data-check` | GitHub Actions → `data-check` step |
| A-03 | Eval gate passes (accuracy ≥ 0.80, F1 ≥ 0.75) | `make eval-gate` | GitHub Actions → `eval-gate` step |
| A-04 | Eval report artifact uploaded | CI artifact upload | GitHub Actions → Artifacts tab |
| A-05 | All CI steps exit with code 0 | Workflow status | PR status checks — all green |

### 👁️ Manual (Required reviewer sign-off in PR description)

| # | Criterion | Evidence Required |
|---|-----------|-------------------|
| M-01 | All 6 spec files present in `/specs` with headings filled in | Reviewer checks file list |
| M-02 | `configs/thresholds.yaml` reflects intended release thresholds | Reviewer reads YAML |
| M-03 | No PII or credentials in committed files | Reviewer + secret scanning |
| M-04 | `reports/eval_report.json` reviewed — no unexpected metric cliffs (> 5% drop vs last release) | Reviewer reads report |
| M-05 | PR description includes: 1-page PRD summary, DoD artifact list, CI link | Reviewer checks PR body |
| M-06 | Spec docs updated to reflect any scope changes in this PR | Reviewer checks git diff |

---

## CI Status Checks Configuration

The following status checks are required on `main` branch:
```
ci / test
ci / data-check  
ci / eval-gate
```

These are defined in `.github/workflows/ci.yml` and enforced via GitHub branch protection rules.

---

## PR Description Template

When submitting a homework PR, include:

```markdown
## 1-Page PRD Summary
[2-3 sentences: what problem, what solution, what success looks like]

## DoD Artifact List
- [ ] A-01: Tests green ✅
- [ ] A-02: Data check green ✅
- [ ] A-03: Eval gate green ✅
- [ ] A-04: Eval report uploaded ✅
- [ ] A-05: All CI green ✅
- [ ] M-01: All 6 specs present ✅
- [ ] M-02: Thresholds reviewed ✅
- [ ] M-03: No PII/secrets ✅
- [ ] M-04: No metric cliffs ✅
- [ ] M-05: PR description complete ✅
- [ ] M-06: Specs updated ✅

## CI Link
[Link to passing CI run]
```

---

## Versioning

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-08 | Initial DoD |
