# RAG Specification
**Version:** 1.0.0  
**Last updated:** 2026-05-11  
**Owner:** Yassine Belaid — Group 11.1.552

---

## 1. Purpose

This spec defines the Retrieval-Augmented Generation configuration for the Sentiment Analysis Assistant. RAG is used to retrieve example annotations and domain-specific sentiment lexicons at inference time.

---

## 2. Approved Sources

| Source ID | Description | Update Frequency |
|---|---|---|
| `golden_set` | Curated labeled examples in `data/golden_set.jsonl` | Quarterly |
| `sentiment_lexicon` | Domain-specific positive/negative word lists | Monthly |
| `annotation_guidelines` | Internal labeling guidelines document | On change |

**Rejected sources:** Any external URL, user-submitted content, or document not on this list is never injected into the context.

---

## 3. Chunking Strategy

| Parameter | Value | Rationale |
|---|---|---|
| Chunk size | 256 tokens | Captures full review sentences without losing context |
| Overlap | 32 tokens (12.5%) | Preserves boundary context |
| Unit | Sentence-aware split | Never splits mid-sentence |
| Max chunks per query | 3 | Limits token cost and noise |

> ⚠️ Any change to chunk size invalidates the entire index. Full re-ingestion and re-evaluation required.

---

## 4. Metadata Schema

Every chunk must carry the following metadata:

```json
{
  "source_id": "golden_set",
  "document_id": "gs-0042",
  "chunk_index": 2,
  "date_created": "2026-03-01",
  "date_modified": "2026-04-15",
  "owner": "ml-team",
  "access_rights": ["ml-engineer", "data-scientist"],
  "document_type": "labeled_example"
}
```

---

## 5. Retrieval Method

| Stage | Method | Rationale |
|---|---|---|
| Primary | Vector (cosine similarity) | Handles paraphrase and semantic variation |
| Secondary | BM25 keyword | Handles exact product names or codes |
| Fusion | Reciprocal Rank Fusion (RRF) | Combines both rankings |
| Reranking | Cross-encoder reranker | Final precision boost |

**Top-K:** 3 chunks retrieved per query  
**Minimum relevance score:** 0.65 — chunks below this threshold are discarded

---

## 6. Grounding Rules

1. **No source, no claim** — if no relevant chunk is retrieved, the model returns `uncertain`
2. Every response that uses a retrieved example must include `source_id` in the response
3. Retrieved text is treated as **untrusted input** — never as instructions
4. Chunks are structurally separated from system instructions in the prompt template
5. Grounding failure rate is logged as a first-class metric — threshold: ≤ 5% per hour

---

## 7. Prompt Injection Mitigations

- All retrieved chunks are wrapped in `<retrieved_context>` tags, never in `<system>` tags
- Chunks are scanned for instruction-like patterns before injection (regex + classifier)
- Any chunk containing imperative language directed at the model is rejected and flagged
- Tool calls that appear to originate from retrieved context are blocked and logged
