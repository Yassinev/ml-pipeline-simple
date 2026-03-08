# Software Requirements Specification (SRS)
**Project:** ML Pipeline Sample  
**Version:** 1.0  
**Date:** 2026-03-08  
**Status:** Draft

---

## 1. Introduction

### 1.1 Purpose
This SRS defines the system-level requirements for the ML pipeline, translating the PRD into testable, implementable specifications.

### 1.2 Scope
Covers the data ingestion layer, validation gates, eval harness, CI integration, and spec documentation.

### 1.3 Definitions
| Term | Definition |
|------|-----------|
| Data Contract | Schema + value-range rules enforced before pipeline runs |
| Eval Gate | Automated threshold check on model metrics |
| DoD | Definition of Done — release-ready checklist |
| CI | Continuous Integration via GitHub Actions |

## 2. System Overview

The system is a Python-based ML pipeline with:
- A data validator (`src/aispec/data_contract.py`)
- An eval gate (`src/aispec/eval_gate.py`)
- A CI workflow (`.github/workflows/ci.yml`)
- Spec documents (`/specs`)

## 3. Functional Requirements

### 3.1 Data Validation
- **FR-DV-01:** The system SHALL reject input files that fail schema validation.
- **FR-DV-02:** The system SHALL log the count of missing, null, and out-of-range fields.
- **FR-DV-03:** The data validator SHALL exit with code `1` on any violation.

### 3.2 Eval Gate
- **FR-EG-01:** The eval gate SHALL read thresholds from `configs/thresholds.yaml`.
- **FR-EG-02:** The eval gate SHALL compare metrics in `reports/metrics_example.json` to thresholds.
- **FR-EG-03:** The eval gate SHALL exit with code `1` if any metric is below its threshold.
- **FR-EG-04:** The eval gate SHALL write a summary report to `reports/eval_report.json`.

### 3.3 CI Pipeline
- **FR-CI-01:** CI SHALL run on every push and pull request to `main`.
- **FR-CI-02:** CI SHALL run steps in order: lint → test → data-check → eval-gate.
- **FR-CI-03:** CI SHALL upload `reports/` as an artifact on both pass and failure.
- **FR-CI-04:** A PR SHALL NOT be mergeable unless all CI steps pass.

### 3.4 Spec & Documentation
- **FR-SP-01:** All six spec templates SHALL be present in `/specs`.
- **FR-SP-02:** `DoD.md` SHALL list all release-ready criteria with CI linkage.

## 4. Non-Functional Requirements

- **NFR-01 Performance:** Data check SHALL complete within 60 seconds for files ≤ 10 MB.
- **NFR-02 Reliability:** CI SHALL have a flakiness rate < 1%.
- **NFR-03 Security:** No credentials SHALL be committed; use GitHub Secrets.
- **NFR-04 Maintainability:** Thresholds SHALL be changeable without modifying Python source.

## 5. External Interfaces

| Interface | Description |
|-----------|-------------|
| GitHub Actions | Executes CI on push/PR events |
| `configs/thresholds.yaml` | Configuration input for eval gate |
| `reports/metrics_example.json` | Metrics input consumed by eval gate |
| `data/sample_requests.jsonl` | Sample data consumed by data validator |

## 6. Acceptance Criteria

All functional requirements are verified by:
- `pytest tests/` — unit tests
- `make data-check` — FR-DV-*
- `make eval-gate` — FR-EG-*
- CI green status — FR-CI-*
- Reviewer spec checklist — FR-SP-*
