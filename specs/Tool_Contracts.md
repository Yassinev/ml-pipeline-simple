# Tool Contracts
**Version:** 1.0.0  
**Last updated:** 2026-05-11  
**Owner:** Yassine Belaid — Group 11.1.552

---

## 1. Tool Allowlist

Only the following tools may be called by the model. Any call to a tool not on this list is **rejected at the orchestrator** before reaching the model.

| Tool | Permission | Confirmation Required |
|---|---|---|
| `classify_text` | Read-only | No |
| `get_model_version` | Read-only | No |
| `log_request` | Write (append-only) | No |
| `flag_for_human_review` | Write | No |
| `update_model` | Write (destructive) | **Yes — explicit user approval** |

---

## 2. Tool Contracts

### 2.1 `classify_text`

```json
{
  "name": "classify_text",
  "permission": "read",
  "confirmation_required": false,
  "parameters": {
    "type": "object",
    "required": ["request_id", "text"],
    "properties": {
      "request_id": { "type": "string", "format": "uuid" },
      "text": { "type": "string", "minLength": 1, "maxLength": 4096 }
    }
  },
  "error_handling": {
    "timeout_ms": 900,
    "retry_policy": "1 retry with 200ms backoff",
    "fallback": "return status=fallback with label=uncertain"
  }
}
```

---

### 2.2 `log_request`

```json
{
  "name": "log_request",
  "permission": "write",
  "confirmation_required": false,
  "parameters": {
    "type": "object",
    "required": ["request_id", "label", "status"],
    "properties": {
      "request_id": { "type": "string", "format": "uuid" },
      "label": { "type": "string", "enum": ["positive","negative","neutral","uncertain"] },
      "status": { "type": "string", "enum": ["ok","fallback","timeout","error"] }
    }
  },
  "notes": "PII must be stripped before this call. Raw text is never logged.",
  "error_handling": {
    "timeout_ms": 200,
    "retry_policy": "fire-and-forget — logging failure does not block response",
    "fallback": "silent drop — log warning metric"
  }
}
```

---

### 2.3 `flag_for_human_review`

```json
{
  "name": "flag_for_human_review",
  "permission": "write",
  "confirmation_required": false,
  "parameters": {
    "type": "object",
    "required": ["request_id", "reason"],
    "properties": {
      "request_id": { "type": "string", "format": "uuid" },
      "reason": {
        "type": "string",
        "enum": ["low_confidence", "pii_detected", "unsafe_input", "ambiguous"]
      }
    }
  },
  "error_handling": {
    "timeout_ms": 300,
    "retry_policy": "1 retry",
    "fallback": "log metric — do not block response"
  }
}
```

---

### 2.4 `update_model` ⚠️ Destructive

```json
{
  "name": "update_model",
  "permission": "write",
  "confirmation_required": true,
  "confirmation_message": "You are about to replace the active model version. This affects all future requests. Confirm? (yes/no)",
  "parameters": {
    "type": "object",
    "required": ["model_version", "approved_by"],
    "properties": {
      "model_version": { "type": "string" },
      "approved_by": { "type": "string", "description": "Email of approving engineer" }
    }
  },
  "error_handling": {
    "timeout_ms": 5000,
    "retry_policy": "no retry — require fresh confirmation",
    "fallback": "abort and return error — never partially update"
  }
}
```

---

## 3. Enforcement Rules

- Any tool not on the allowlist → **rejected at orchestrator, attempt logged**
- Write tools called without valid parameters → **rejected, error returned to model**
- `update_model` called without confirmation in the same session → **rejected**
- All tool calls logged with originating `request_id` for full traceability
