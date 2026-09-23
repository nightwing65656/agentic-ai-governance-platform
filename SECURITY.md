# Security and Control Overview

This document describes the security and control posture of the Agentic AI Governance & Observability Platform, with a focus on audit integrity, evidence quality, and operational transparency for institutional adopters.

## What this platform protects

- **Audit log integrity**: Tamper-evident, hash-chained JSONL logs that record agent events with a structured 24-field schema.
- **Evidence quality**: Instrumentation that captures operational, cognitive, and contextual signals for each agent run.
- **Control visibility**: Security scanning of agent configurations and code paths (tool boundaries, credentials, MCP-style configs).
- **Compliance readiness**: Regulator-ready reports derived directly from immutable audit logs.

## Threat model (high level)

We assume:

- **Trusted**: The host environment where the platform runs (CI, controlled VM, or container) is managed by the adopting organization.
- **Untrusted / partially trusted**:
  - External tools and APIs invoked by agents.
  - Third-party models and prompts.
  - Users who can trigger agent runs but should not be able to alter past audit records without detection.

Key risks addressed:

- **Tampering with audit logs**: Mitigated via SHA-256 hash chaining and integrity verification.
- **Undetected misconfigurations**: Mitigated via static and config scans (credential patterns, tool-boundary rules, MCP-like configs).
- **Opaque agent behavior**: Mitigated via structured, multi-dimensional logging and report generation.

## Control objectives and EU AI Act alignment

The platform supports controls relevant to **EU AI Act Article 12** (record-keeping / logging) for high-risk AI systems:

- **Traceability**: Each agent run is logged with structured events, timestamps, and surface types.
- **Integrity**: Hash-chained logs make post-hoc tampering detectable.
- **Reviewability**: Compliance reports can be generated from audit logs for internal/external review.

Organizations can map these capabilities to their own control frameworks (e.g., model risk management, third-party risk, operational resilience).

## Operational guidance

For teams deploying or integrating this platform:

- Run the platform in a **controlled environment** with restricted write access to audit log storage.
- Treat `audit_logs.jsonl` (or equivalent) as **immutable append-only evidence**; do not manually edit.
- Integrate **periodic integrity checks** (e.g., scheduled runs of the demo or a dedicated integrity script) into your operations.
- Use the **security scanner** as part of your pre-deployment checks for new agent configurations or tool integrations.
- Do **not** commit secrets, credentials, or sensitive data into the repository or logs.

## Limitations

This platform is a **control and observability layer**, not a full security boundary:

- It does not replace network security, IAM, or secrets management.
- It does not guarantee absence of vulnerabilities in underlying models or tools.
- It provides evidence and detection aids, not absolute prevention.

Organizations should integrate this platform into a broader AI governance and risk management program.

## Reporting security issues

If you discover a security-relevant issue (e.g., a way to bypass tamper-evidence, a critical flaw in the scanner, or a serious logging gap), please report it responsibly:

- Open a GitHub issue with a clear description and minimal reproduction steps, or
- Contact the maintainer directly if public disclosure is not yet appropriate.

We will prioritize issues affecting audit integrity and control reliability.