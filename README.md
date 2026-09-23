# Agentic AI Governance & Observability Platform

**License:** Source-available for non-commercial research and evaluation use only. Commercial, production, or revenue-generating use requires a separate commercial license from Dheeraj Krishna Kumar. [Contact for commercial licensing](./CONTACT.md).

**Disclaimer:** This project is for informational and educational purposes only. It does not constitute investment, tax, or legal advice. No buy, sell, hold, ranking, or suitability recommendations are made. Human review is required before any output is used. [Full disclaimer](./DISCLAIMER.md).

**Research foundations:** This project implements concepts from AgentTrace (AAAI 2026) and Agent Audit (ACM AIES 2026), adapted for financial-services governance and EU AI Act Article 12 compliance. [1][2]

---

## Overview

A Python-native, financial-services-focused agentic AI governance platform implementing:

- **AgentTrace-style structured observability** — Operational, cognitive, and contextual trace surfaces with OpenTelemetry integration. [1]
- **Agent Audit-style pre-deployment security scanning** — Tool-boundary detection, credential scanning, MCP configuration security checks. [2]
- **EU AI Act Article 12-compliant tamper-evident audit trails** — SHA-256 hash-chained event logs with regulator-ready report generation. [3]

This project is designed to demonstrate production-grade agentic AI governance competencies for senior AI engineering roles in financial services and regulated environments.

---

## What This Project Is (and Is Not)

**This project is:**
- A governance and observability layer for LLM-based agentic workflows.
- A demonstration of engineering rigor in non-deterministic AI systems.
- A portfolio artifact positioning the author for senior AI engineering roles in financial services.

**This project is not:**
- A trading system, investment adviser, market-prediction engine, or recommendation tool.
- Affiliated with, endorsed by, or representative of BlackRock, Aladdin, Vanguard, or any fund manager.
- A substitute for professional legal, tax, or investment advice.
- A generic observability tool — explicitly scoped to agentic AI systems with cognitive, operational, and contextual trace surfaces. [1]

---

## Quick Start (Local Development)

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run security scan on sample agent
python -m src.security.agent_audit examples/sample_agent.py

# Run instrumentation demo
python -m src.main --demo

# Generate sample compliance report
python -m src.main --generate-report --input examples/sample_audit_log.jsonl --output examples/sample_compliance_report.md
```

---

## Key Features (v0.1.0)

- **Structured audit log schema** — 24-field Pydantic model aligned with EU AI Act Article 12 requirements. [3]
- **Tamper-evident hash chaining** — SHA-256 hash-chained JSONL logs with integrity verification. [3]
- **AgentTrace-style instrumentation** — Decorators for operational, cognitive, contextual logging. [1]
- **Agent Audit-style security scanner** — Tool-boundary detection, credential scanning, MCP config checks. [2]
- **Regulator-ready report generation** — CSV/PDF compliance reports for any agent run. [3]
- **GitHub Actions CI** — pytest, Ruff, security scan, disclaimer-presence checks on every push.

---

## Repository Structure
agentic-ai-governance-platform/
├── .github/
│ └── workflows/
│ └── ci.yml
├── docs/
│ ├── architecture.md
│ ├── data-governance.md
│ └── evidence-schema.md
├── examples/
│ ├── sample_agent.py
│ ├── sample_config.yaml
│ ├── sample_audit_log.jsonl
│ └── sample_compliance_report.md
├── src/
│ ├── schemas/
│ │ └── audit_log.py
│ ├── instrumentation/
│ │ └── agent_trace.py
│ ├── security/
│ │ └── agent_audit.py
│ ├── audit/
│ │ └── tamper_evident_logger.py
│ ├── report/
│ │ └── compliance_report.py
│ └── main.py
├── tests/
│ ├── test_schemas.py
│ ├── test_instrumentation.py
│ ├── test_security.py
│ ├── test_tamper_evident.py
│ └── test_compliance_report.py
├── ABOUT.md
├── CONTACT.md
├── DISCLAIMER.md
├── COMMERCIAL_LICENSE_TERMS.md
├── LICENSE
├── README.md
├── requirements.txt
└── .env.example
---

## Research Citations

[1] AgentTrace: A Structured Logging Framework for Agent System Observability (AAAI 2026 Workshop). https://arxiv.org/abs/2602.10133

[2] Agent Audit: A Security Analysis System for LLM Agent Applications (ACM AIES 2026). https://arxiv.org/abs/2603.22853

[3] EU AI Act Article 12: Record-Keeping Requirements. https://artificialintelligenceact.eu/article/12/

---

## Non-Affiliation Notice

This project is an independent, individual-developer work.

---

## License Summary

- **Non-commercial use:** Permitted for research, evaluation, and educational purposes with mandatory attribution.
- **Commercial use:** Requires a separate commercial license from Dheeraj Krishna Kumar. [Contact for commercial licensing](./CONTACT.md).
- **Attribution:** Required in all copies, derivatives, and documentation.

See [LICENSE](./LICENSE) and [COMMERCIAL_LICENSE_TERMS.md](./COMMERCIAL_LICENSE_TERMS.md) for full terms.
