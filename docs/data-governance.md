# Data Governance

## Overview

This document describes the data governance principles and practices for the Agentic AI Governance & Observability Platform. It addresses data provenance, retention, privacy, and compliance considerations.

## Data Types Handled

### 1. Audit Log Data

**Description:** Structured records of agent execution events (operational, cognitive, contextual traces).

**Fields include:**
- Timestamps, agent IDs, method names, durations.
- LLM model identifiers, prompt/output fingerprints (not raw content if PII).
- Tool calls, policy check results, human approver IDs.
- Hash-chain fields for tamper evidence.

**Retention:** Configurable via `retention_category` field (`standard`, `extended`, `legal_hold`).

**Privacy:** Sensitive fields (e.g., prompts, outputs) are stored as fingerprints/hashes, not raw content, to avoid PII exposure. [1]

### 2. Security Scan Results

**Description:** Findings from pre-deployment security analysis of agent code.

**Fields include:**
- Vulnerability type, confidence score, location (file:line).
- Remediation guidance.

**Retention:** Stored alongside audit logs for compliance reporting.

**Privacy:** No PII; purely code-level metadata.

### 3. Configuration Data

**Description:** MCP-style configuration files, environment variables.

**Fields include:**
- Tool definitions, API endpoints, credential references.

**Retention:** Version-controlled alongside agent code.

**Privacy:** Credentials should be stored in environment variables or secrets managers, not in config files.

## Data Provenance

Every audit log entry includes:

- `source_document_id` / `agent_id`: Identifies the agent that produced the event.
- `timestamp`: UTC timestamp of the event.
- `trace_id` / `span_id`: Hierarchical tracing for grouping related events.
- `previous_log_hash` / `current_log_hash`: Tamper-evident chaining.

This ensures full traceability from any report back to the original agent execution.

## EU AI Act Article 12 Compliance

The platform implements the following Article 12 minimum fields: [1]

- **Use period:** Captured via `timestamp` fields.
- **Reference database:** Captured via `agent_id` and configuration metadata.
- **Input data:** Captured via `input_fingerprint` (hash, not raw content).
- **Verifier identity:** Captured via `human_approver_id` when human review occurs.

## Data Retention Policy

**Default retention:** 90 days for `standard` category, 1 year for `extended`, indefinite for `legal_hold`.

**Deletion:** Logs are automatically purged after retention period expires (future feature).

**Export:** Logs can be exported to external storage (e.g., S3, GCS) for long-term archival.

## Privacy and PII Handling

**Principle:** Minimize storage of raw PII. Use fingerprints/hashes where possible.

**Implementation:**
- `prompt_template_id` references a template, not full prompt content.
- `input_fingerprint` and `output_fingerprint` are SHA-256 hashes, not raw payloads.
- Human approver IDs are stored, but not full names or contact details (unless explicitly configured).

**Recommendation:** Do not log raw user inputs or outputs containing PII. Use hashing or redaction before logging.

## Security Controls

- **Tamper-evident logging:** SHA-256 hash chaining detects any modification.
- **Access control:** Future versions may include role-based access to audit logs.
- **Encryption at rest:** Logs should be stored on encrypted filesystems or cloud storage.
- **Encryption in transit:** OpenTelemetry export uses TLS by default.

## References

[1] EU AI Act Article 12: Record-Keeping Requirements. https://artificialintelligenceact.eu/article/12/
