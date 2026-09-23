# Control Summary

This document summarizes the primary controls provided by the Agentic AI Governance & Observability Platform and how they map to typical control objectives for high-risk AI systems (e.g., EU AI Act Article 12–style record-keeping expectations).

## Control objectives and platform capabilities

| Control objective                              | Platform capability                                                                 | Evidence artifact                          |
|-----------------------------------------------|--------------------------------------------------------------------------------------|--------------------------------------------|
| **Tamper-evident audit logging**              | SHA-256 hash-chained JSONL logs with integrity verification                          | `audit_logs.jsonl` + integrity check       |
| **Traceability of agent runs**                | Structured 24-field audit log schema capturing operational, cognitive, contextual events | Audit log entries per agent method/event   |
| **Detection of misconfigurations**            | Static and config scanning for tool boundaries, credential patterns, MCP-style configs | Security scan reports (`--scan`)           |
| **Reviewability for internal/external audit** | Regulator-ready compliance reports generated from immutable audit logs               | CSV/PDF compliance reports                 |
| **Operational visibility**                    | Multi-dimensional logging (method start/complete/error, prompts, completions, errors) | Audit log entries with surface types       |
| **Dependency risk monitoring**                | CI integration of `pip-audit` to detect known vulnerabilities in Python dependencies   | CI `security-audit` job output             |

## How controls are enforced

- **Append-only, hash-chained logs**: Each new entry includes the hash of the previous entry; any modification breaks the chain and is detected by integrity verification.
- **Structured schema**: All events conform to a Pydantic-validated schema, reducing the risk of incomplete or inconsistent records.
- **Automated checks in CI**: Every push/pull request runs tests, lint, type checking (mypy), and dependency auditing (pip-audit).
- **Separation of duties**: The platform provides evidence and detection aids; it does not replace IAM, network security, or secrets management.

## Limitations and scope

- This platform is an **observability and control layer**, not a full security boundary.
- It does **not** guarantee absence of vulnerabilities in underlying models, tools, or infrastructure.
- It provides **detective** and **deterrent** controls, not absolute prevention.

Organizations should integrate these capabilities into their broader AI governance, model risk management, and third-party risk programs.