# About This Project

## Purpose

The Agentic AI Governance & Observability Platform is a portfolio-quality project designed to demonstrate production-grade competencies in:

- Agentic AI system architecture
- Non-deterministic system observability
- Security scanning for LLM agent applications
- EU AI Act Article 12-compliant audit trail implementation
- Financial-services-focused governance and compliance reporting

This project is intended to position the author (Dheeraj Krishna Kumar) for senior AI engineering and architecture roles in financial services and regulated environments.

## Research Foundations

This project implements and adapts concepts from:

1. **AgentTrace** (AAAI 2026 Workshop) — Structured logging framework with operational, cognitive, and contextual trace surfaces. [1]
2. **Agent Audit** (ACM AIES 2026) — Security analysis system for LLM agent applications with tool-boundary detection and credential scanning. [2]
3. **EU AI Act Article 12** — Record-keeping requirements for high-risk AI systems, including tamper-evident logging and specific field requirements. [3]

## Author

**Dheeraj Krishna Kumar**  
AI Engineer & Technology Consultant  
MTech in Data Science & Artificial Intelligence  
LinkedIn: https://www.linkedin.com/in/dheeraj-krishna-kumar/  
GitHub: https://github.com/nightwing65656

## Non-Affiliation Notice

This project is an independent, individual-developer work. It is not affiliated with, endorsed by, or representative of BlackRock, Aladdin, Vanguard, or any other investment manager or technology provider. References to BlackRock/Aladdin are solely as an inspirational quality benchmark for engineering rigor.

## Version

**v0.1.0** — Initial MVP release with:
- Audit log schema (24 fields, Pydantic-validated)
- Tamper-evident hash-chained JSONL logging
- AgentTrace-style instrumentation (operational, cognitive, contextual)
- Agent Audit-style security scanner (tool-boundary, credential, MCP config)
- Regulator-ready compliance report generation
- GitHub Actions CI (pytest, Ruff, security scan, disclaimer checks)

See [README.md](./README.md) for quick start and [docs/architecture.md](./docs/architecture.md) for technical details.
