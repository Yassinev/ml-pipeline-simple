# Incident Playbook
**Version:** 2.0.0  
**Last updated:** 2026-05-11  
**Owner:** Yassine Belaid — Group 11.1.552

---

## Scenario 1 — Data Exposure (PII Leaked in Logs)

### Detection
- Automated PII scan alert on log store (Presidio daily scan)
- User complaint about personal data visible in response
- SIEM alert from security monitoring

### Roles
| Role | Person | Action |
|---|---|---|
| Incident Commander | Engineering Owner | Coordinates response |
| Security Lead | Security Owner | Assesses scope of exposure |
| Communications | Product Risk Owner | Notifies affected users if required |

### Response Steps
1. **Contain (0–15 min):** Disable logging pipeline — `make disable-logging`
2. **Assess (15–60 min):** Query log store for PII patterns — identify affected `request_id` range
3. **Remediate (1–4 hrs):** Delete affected log entries — run `scripts/purge_pii_logs.sh`
4. **Fix (4–24 hrs):** Patch Presidio redaction middleware — deploy fix — re-enable logging
5. **Review (24–72 hrs):** Post-incident report — update redaction rules — add regression test

### Post-Incident Requirements
- Written report filed in `specs/incidents/`
- New red-team prompt added covering the leak pattern
- CI gate updated to catch regression

---

## Scenario 2 — Tool Misuse (Unauthorized Tool Call Executed)

### Detection
- Orchestrator alert: non-allowlisted tool called
- Spike in write tool calls detected by anomaly monitoring
- User reports unexpected side effect

### Roles
| Role | Person | Action |
|---|---|---|
| Incident Commander | Engineering Owner | Coordinates response |
| Security Lead | Security Owner | Forensic analysis of tool call logs |
| Product Owner | Product Risk Owner | Assesses business impact |

### Response Steps
1. **Contain (0–10 min):** Disable all write tools — set `allowlist.write_enabled = false`
2. **Assess (10–30 min):** Review tool call logs — identify originating `request_id` and prompt
3. **Remediate (30–120 min):** Reverse any unauthorized side effects if possible
4. **Fix (2–8 hrs):** Patch orchestrator tool validation — add missing confirmation gate
5. **Review (24–48 hrs):** Post-incident report — update Tool_Contracts.md — add regression test

### Post-Incident Requirements
- Tool call logs preserved as evidence
- Allowlist validation logic reviewed and hardened
- New red-team prompt added for the injection vector used

---

## Scenario 3 — Model Safety Regression (Refusal Behavior Broken)

### Detection
- CI red-team gate fails on PR — merge blocked
- Production refusal rate drops > 20% below baseline
- User reports model complying with unsafe request

### Roles
| Role | Person | Action |
|---|---|---|
| Incident Commander | Engineering Owner | Coordinates response, owns rollback decision |
| ML Lead | Engineering Owner | Investigates prompt change that caused regression |
| Product Owner | Product Risk Owner | Assesses user impact |

### Response Steps
1. **Contain (0–5 min):** Roll back to previous model version — `make rollback-model`
2. **Assess (5–30 min):** Identify which prompt change caused regression — `git log specs/Prompt_Behavior_Spec.md`
3. **Reproduce (30–60 min):** Run full red-team suite against failing version — document failures
4. **Fix (1–4 hrs):** Revert prompt change OR patch behavior spec — re-run full suite
5. **Review (24–48 hrs):** Post-incident report — add new prompts — update CI gate

### Post-Incident Requirements
- Root cause documented: which prompt edit caused regression
- CI gate updated to catch this regression class permanently
- Prompt_Behavior_Spec.md version bumped with change log entry

---

## Escalation Path

```
On-call Engineer
      ↓ (if unresolved in 30 min)
Engineering Owner
      ↓ (if data exposure or user impact)
Security Owner + Product Risk Owner
      ↓ (if regulatory obligation)
Course Instructor / Compliance Officer
```
