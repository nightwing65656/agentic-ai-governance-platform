# Architecture

## Overview

The Agentic AI Governance & Observability Platform follows a modular, layered architecture designed for:

- **Separation of concerns** — Each module has a single, well-defined responsibility.
- **Testability** — All components are independently testable with clear interfaces.
- **Extensibility** — New trace surfaces, security checks, or report formats can be added without modifying core logic.

## System Components

### 1. Schema Layer (`src/schemas/`)

**Purpose:** Define validated data structures for audit logs and related artifacts.

**Key module:** `audit_log.py`

- 24-field Pydantic model for audit log entries.
- Aligned with EU AI Act Article 12 requirements. [1]
- Includes tamper-evident hash-chaining fields (`previous_log_hash`, `current_log_hash`).

### 2. Instrumentation Layer (`src/instrumentation/`)

**Purpose:** Capture structured traces from agent execution.

**Key module:** `agent_trace.py`

- Implements AgentTrace's three-surface taxonomy: [2]
  - **Operational traces:** Method calls, timing, errors.
  - **Cognitive traces:** LLM prompts, completions, reasoning chains.
  - **Contextual traces:** HTTP, DB, cache I/O via OpenTelemetry auto-instrumentation.
- Provides decorators and context managers for easy integration.

### 3. Security Layer (`src/security/`)

**Purpose:** Pre-deployment security scanning for agent code.

**Key module:** `agent_audit.py`

- Implements Agent Audit-style analysis: [3]
  - Tool-boundary detection.
  - Intra-procedural taint analysis.
  - Credential detection.
  - MCP configuration security checks.
- Outputs JSON report with confidence-scored findings.

### 4. Audit Layer (`src/audit/`)

**Purpose:** Tamper-evident logging and integrity verification.

**Key module:** `tamper_evident_logger.py`

- SHA-256 hash-chained JSONL logging.
- Append-only storage with integrity verification.
- Supports OpenTelemetry export for distributed tracing.

### 5. Report Layer (`src/report/`)

**Purpose:** Generate regulator-ready compliance reports.

**Key module:** `compliance_report.py`

- Produces Markdown/CSV/PDF reports from audit logs.
- Includes EU AI Act Article 12 minimum fields. [1]
- Human-review notice and disclaimer injection.

### 6. CLI Entry Point (`src/main.py`)

**Purpose:** Command-line interface for running demos, scans, and report generation.

**Commands:**
- `--demo`: Run instrumentation demo with sample agent.
- `--scan <path>`: Run security scan on agent code.
- `--generate-report --input <log> --output <report>`: Generate compliance report.

## Data Flow
Agent Code → Instrumentation → Audit Log (JSONL) → Compliance Report
↓
Security Scanner (pre-deployment)
1. Agent code is instrumented with decorators/context managers.
2. Execution produces structured audit logs (operational, cognitive, contextual).
3. Logs are hash-chained and stored in append-only JSONL.
4. Compliance reports are generated from logs with citations and disclaimers.

## Security Considerations

- **Tamper-evident logging:** Hash chaining detects any modification to audit logs.
- **Credential scanning:** Pre-deployment scans detect hardcoded secrets.
- **Access control:** Future versions may include role-based access to audit logs.

## References

[1] EU AI Act Article 12: Record-Keeping Requirements. https://artificialintelligenceact.eu/article/12/

[2] AgentTrace: A Structured Logging Framework for Agent System Observability (AAAI 2026). https://arxiv.org/abs/2602.10133

[3] Agent Audit: A Security Analysis System for LLM Agent Applications (ACM AIES 2026). https://arxiv.org/abs/2603.22853
