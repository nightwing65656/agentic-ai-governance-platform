# Evidence Schema (Audit Log Entry Schema)

## Overview

This document describes the 24-field audit log entry schema implemented in `src/schemas/audit_log.py`. The schema is aligned with EU AI Act Article 12 requirements and AgentTrace's three-surface taxonomy. [1][2]

## Schema Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `log_id` | UUID | Yes | Unique identifier for this log entry. |
| `trace_id` | UUID | Yes | Groups related events across surfaces (AgentTrace concept). [2] |
| `span_id` | UUID | Yes | Hierarchical span within trace. |
| `surface_type` | Enum | Yes | One of: `operational`, `cognitive`, `contextual`. [2] |
| `event_type` | Enum | Yes | One of: `method_start`, `method_complete`, `method_error`, `llm_prompt`, `llm_completion`, `tool_call`, `db_query`, `http_request`, `policy_check`, `human_approval`. |
| `timestamp` | datetime (UTC, ISO-8601) | Yes | EU AI Act Article 12 requirement. [1] |
| `agent_id` | str | Yes | Identifier for the agent instance. |
| `agent_name` | str | Yes | Human-readable name. |
| `method_name` | str | No | For operational events. |
| `duration_ms` | int | No | Execution duration for completed methods. |
| `llm_model` | str | No | e.g. `"gpt-4o-2024-11-20"` — EU AI Act requires model + version. [1] |
| `prompt_template_id` | str | No | Reference to prompt template (not full content, per privacy guidance). [1] |
| `input_fingerprint` | str | No | Hash or summarization of input (not raw payload if PII). [1] |
| `output_fingerprint` | str | No | Hash or summarization of output. |
| `tool_calls` | list[dict] | No | Each with `tool_name`, `arguments`, `result`. |
| `policy_check_result` | Enum | No | One of: `allowed`, `blocked`, `requires_approval`. |
| `human_approver_id` | str | No | EU AI Act: identification of natural persons involved in verification. [1] |
| `human_approval_timestamp` | datetime | No | When approver signed off. [1] |
| `override_flag` | bool | No | Whether human overrode AI output. [1] |
| `decision_outcome` | Enum | Yes | One of: `success`, `failure`, `deferred`, `escalated`, `rejected`. |
| `error_message` | str | No | If applicable. |
| `confidence_score` | float (0.0–1.0) | No | If model emits one. [1] |
| `token_count` | int | No | For cost tracking and anomaly detection. [1] |
| `previous_log_hash` | str (SHA-256) | Yes | Hash of prior log entry (tamper-evident chaining). [1] |
| `current_log_hash` | str (SHA-256) | Yes | Hash of this entry (computed after serialization). |
| `retention_category` | Enum | Yes | One of: `standard`, `extended`, `legal_hold`. |

## EU AI Act Article 12 Mapping

| Article 12 Requirement | Schema Field(s) |
|---|---|
| Automatic recording of events | All fields, especially `timestamp`, `event_type`, `agent_id`. [1] |
| Use period | `timestamp` fields. [1] |
| Reference database | `agent_id`, configuration metadata. [1] |
| Input data | `input_fingerprint` (hash, not raw content). [1] |
| Verifier identity | `human_approver_id`. [1] |
| Tamper-evident storage | `previous_log_hash`, `current_log_hash`. [1] |

## AgentTrace Three-Surface Mapping

| Surface Type | Example Events |
|---|---|
| `operational` | `method_start`, `method_complete`, `method_error`, `tool_call`. [2] |
| `cognitive` | `llm_prompt`, `llm_completion`, `policy_check`. [2] |
| `contextual` | `db_query`, `http_request`, `human_approval`. [2] |

## Validation Rules

- `log_id`, `trace_id`, `span_id` must be valid UUIDs.
- `timestamp` must be UTC, ISO-8601 formatted.
- `surface_type`, `event_type`, `decision_outcome`, `retention_category` must be valid enum values.
- `confidence_score` must be between 0.0 and 1.0 (if present).
- `previous_log_hash` and `current_log_hash` must be valid SHA-256 hex strings (64 characters).
- `current_log_hash` is computed after serialization and must match recomputation on verification.

## Example Entry (JSON)

```json
{
  "log_id": "550e8400-e29b-41d4-a716-446655440000",
  "trace_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "span_id": "6ba7b812-9dad-11d1-80b4-00c04fd430c8",
  "surface_type": "cognitive",
  "event_type": "llm_completion",
  "timestamp": "2026-09-22T10:30:00Z",
  "agent_id": "agent-001",
  "agent_name": "ResearchAgent",
  "llm_model": "gpt-4o-2024-11-20",
  "prompt_template_id": "template-research-v1",
  "input_fingerprint": "a3f2b8c1d4e5f6...",
  "output_fingerprint": "b4g3c9d2e5f7g8...",
  "token_count": 1500,
  "confidence_score": 0.85,
  "decision_outcome": "success",
  "previous_log_hash": "0000000000000000000000000000000000000000000000000000000000000000",
  "current_log_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "retention_category": "standard"
}
```

## References

[1] EU AI Act Article 12: Record-Keeping Requirements. https://artificialintelligenceact.eu/article/12/

[2] AgentTrace: A Structured Logging Framework for Agent System Observability (AAAI 2026). https://arxiv.org/abs/2602.10133
