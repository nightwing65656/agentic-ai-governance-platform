# Release Notes – v0.1.0 (September 2026)

This is the initial public release of the **Agentic AI Governance & Observability Platform**, a Python-native, financial-services-focused governance layer for LLM-based agentic workflows.

## Purpose and positioning

This release demonstrates a production-grade approach to governing non-deterministic AI agents in regulated environments. It is designed as:

- A **portfolio artifact** positioning the author for senior AI engineering roles in financial services and regulated industries.
- A **reference implementation** of research concepts from AgentTrace (AAAI 2026) and Agent Audit (ACM AIES 2026), adapted for EU AI Act Article 12–style record-keeping and control objectives.
- A **pilot-ready codebase** that teams can run locally or in containers to evaluate governance, observability, and security controls for agentic AI.

## What’s included in v0.1.0

### Core capabilities

- **Structured audit logging**  
  - 24-field Pydantic schema for agent events (operational, cognitive, contextual).  
  - Tamper-evident, SHA-256 hash-chained JSONL logs with integrity verification.

- **AgentTrace-style instrumentation**  
  - Decorators and context managers for method-level, prompt/completion, and resource-level tracing.  
  - OpenTelemetry integration with console and OTLP exporters.

- **Agent Audit-style security scanning**  
  - Static and config scanning for tool boundaries, credential patterns, and MCP-style configurations.  
  - CLI: `agent-governance --scan <path>`.

- **Compliance reporting**  
  - Generation of regulator-ready reports (Markdown/CSV) from audit logs.  
  - Mapping of events to EU AI Act Article 12–style record-keeping expectations.

### Developer experience and quality gates

- **Packaging**: `pyproject.toml` with editable install, wheel build, and `agent-governance` CLI.
- **Tests**: 35 passing tests covering schemas, instrumentation, security, tamper-evidence, and reporting.
- **Lint & types**: Ruff and mypy clean across `src` and `examples`.
- **Security**: `pip-audit` integrated; no known vulnerabilities in dependencies at time of release.
- **CI**: GitHub Actions workflow enforcing tests, lint, type checking, and dependency auditing on every push.

### Documentation and controls

- **User-facing docs**: `README.md`, `ABOUT.md`, architecture and data-governance docs.
- **Control documentation**:
  - `SECURITY.md`: threat model, control objectives, EU AI Act alignment, operational guidance.
  - `docs/controls.md`: one-page control summary table for risk/compliance reviewers.
  - `docs/operations.md`: guidance on deployment, audit-log management, OpenTelemetry integration, and operational controls.
- **Release discipline**: `CHANGELOG.md`, `CONTRIBUTING.md` with a release checklist.

### Example workloads

- **Instrumentation demo**: `agent-governance --demo`
- **OpenTelemetry tracing demo**: `python -m examples.otel_tracing_demo`
- **Security scan demo**: `agent-governance --scan examples/sample_agent.py`
- **Compliance report demo**: `agent-governance --generate-report --input <log> --output <report>`

## Known limitations and scope

- v0.1.0 is **pilot- and evaluation-focused**, not a hardened production system.
- The platform provides **detective and deterrent controls**, not absolute prevention.
- It does not replace:
  - Network security, IAM, secrets management, or infrastructure hardening.
  - Organizational model risk management, third-party risk, or operational resilience frameworks.

Organizations should integrate this platform into their broader AI governance and risk programs.

## What’s next (future milestones)

Indicative directions for future releases:

- Richer security rules (e.g., data-exfiltration patterns, prompt-injection heuristics).
- Multi-agent and workflow-level observability (orchestrator spans, cross-agent correlation).
- Deeper integrations with specific LLM frameworks and agent libraries.
- Enhanced reporting (PDF, configurable templates, control-mapping overlays).
- Optional “governance service” mode with scheduled scans and centralized audit-log storage.

## Acknowledgments

This work builds on publicly available research (AgentTrace, Agent Audit) and the author’s experience designing systems for regulated environments. It is an independent, individual-developer project.

For licensing terms, see [LICENSE](../LICENSE) and [COMMERCIAL_LICENSE_TERMS.md](../COMMERCIAL_LICENSE_TERMS.md). For inquiries about commercial use or collaboration, see [CONTACT.md](../CONTACT.md).