# ModelSpec — AI Spec Pack

**Version:** 1.0.0  
**Last updated:** 2026-04-19

---

## 1. Task Definition

**Task type:** Multi-class text classification  
**Classes:** `positive`, `negative`, `neutral`  
**Input:** raw UTF-8 text string (1–4096 chars)  
**Output:** predicted class label + confidence score ∈ [0, 1]

---

## 2. Baseline

| Baseline | Description | Expected Macro-F1 |
|---|---|---|
| Majority class | Always predicts the most frequent class | ~0.17 (3-class uniform) |
| TF-IDF + Logistic Regression | Bag-of-words + linear classifier | ~0.72 |
| **Target model** | Fine-tuned transformer (e.g. DistilBERT) | ≥ 0.85 |

The target model must beat the TF-IDF baseline by at least **+0.10 Macro-F1** to be eligible for production.

---

## 3. Applicability Limits

| Dimension | In Scope | Out of Scope |
|---|---|---|
| Language | English (`en-*`) | All other languages |
| Text length | 1–4096 chars | Zero-length; > 4096 chars |
| Domain | General consumer text | Medical, legal, financial advice |
| User tier | All tiers | None excluded |
| Temporal | Data ≤ 1 year old | Data > 3 years old without revalidation |

The model **must not** be used to make autonomous decisions with irreversible real-world consequences.

---

## 4. Resource Envelope

| Resource | Limit | Notes |
|---|---|---|
| Inference RAM | ≤ 2 GB | Per replica |
| GPU VRAM | ≤ 4 GB | Optional; CPU fallback allowed |
| Model artifact size | ≤ 500 MB | On-disk, compressed |
| Cold-start time | ≤ 10 s | From container start to first request |
| Replicas (min/max) | 1 / 10 | Horizontal scaling |

---

## 5. Update Policy

| Trigger | Action | Approval Required |
|---|---|---|
| Macro-F1 drops > 3 % vs previous release | Automatic retraining pipeline | ML Lead sign-off |
| New data batch available (≥ 5 000 samples) | Optional fine-tune | ML Lead sign-off |
| Security vulnerability in dependencies | Patch release < 48 h | Infra Lead sign-off |
| Breaking schema change in data contract | Full retrain + re-eval | ML Lead + Data Eng sign-off |
| Calendar-based refresh | Quarterly retraining | ML Lead sign-off |

All model releases must pass `make eval-gate` before deployment.

---

## 6. Model Card Summary

| Field | Value |
|---|---|
| Model family | Transformer (DistilBERT-base-uncased) |
| Parameters | ~66 M |
| Training framework | PyTorch + HuggingFace Transformers |
| Fairness evaluation | Not yet conducted (planned v1.1) |
| Known failure modes | Sarcasm, very short texts (<10 chars), code snippets |
