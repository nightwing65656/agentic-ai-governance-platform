# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-09-23

### Added

- Initial release of the Agentic AI Governance & Observability Platform.
- Core components:
  - Structured audit log schema (24-field Pydantic model).
  - Tamper-evident hash-chained JSONL logging.
  - AgentTrace-style instrumentation (operational, cognitive, contextual).
  - Agent Audit-style security scanner (tool-boundary, credential, MCP config checks).
  - Regulator-ready compliance report generation (CSV/PDF).
- CLI entry point: `agent-governance` with `--demo`, `--scan`, and `--generate-report` commands.
- GitHub Actions CI: pytest, Ruff, and pip-audit on every push.
- Python packaging via `pyproject.toml` (editable install, wheel build).

### Fixed

- Documentation updated to accurately reflect CI checks (pytest, Ruff, pip-audit).
- `examples` module packaged correctly so the demo runs via the installed CLI.