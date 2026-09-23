# Operating This Platform in Production

This document provides high-level guidance for teams operating the Agentic AI Governance & Observability Platform in pilot or production environments. It is not a substitute for your organization’s security, change-management, or operational-risk policies.

## Deployment options

### Docker-based deployment (recommended for pilots)

The repository includes a minimal `Dockerfile` and `docker-compose.yml` intended for evaluation and pilot deployments.

Basic usage:

```bash
# Build the image
docker build -t agentic-governance:0.1.0 .

# Run a simple demo + scan
docker run --rm agentic-governance:0.1.0
```

For a more structured setup, use `docker-compose`:

```bash
docker compose up
```

This runs the `governance` service defined in `docker-compose.yml`, mounting a local `audit_logs_container` directory for persistent audit logs.

### Direct installation (non-containerized)

Alternatively, install the platform directly in a managed Python environment:

```bash
python -m pip install ".[dev]"
```

Then invoke commands such as:

```bash
agent-governance --demo
agent-governance --scan path/to/agent_or_config
agent-governance --generate-report --input audit_logs.jsonl --output report.md
```

## Audit log management

- Treat `audit_logs*.jsonl` files as **immutable append-only evidence**. Do not manually edit them.
- Store audit logs on storage with:
  - Access controls (least privilege, role-based access).
  - Regular backups and retention policies aligned with your regulatory requirements.
- Periodically verify integrity:

  ```bash
  python -m src.main --demo
  ```

  or implement a scheduled job that loads the log and calls `TamperEvidentLogger.verify_integrity()`.

## OpenTelemetry integration

The platform emits OpenTelemetry spans alongside audit logs. To send traces to your existing observability stack:

1. Deploy an OTLP-compatible collector (e.g., Grafana Tempo, Jaeger, Datadog, etc.).
2. Set environment variables when running the container or CLI:

   ```bash
   OTEL_EXPORTER_OTLP_ENDPOINT=http://your-otlp-collector:4317 \
   OTEL_SERVICE_NAME=agentic-governance-prod \
   agent-governance --demo
   ```

   In `docker-compose.yml`, configure under `environment:`:

   ```yaml
   environment:
     OTEL_EXPORTER_OTLP_ENDPOINT: http://your-otlp-collector:4317
     OTEL_SERVICE_NAME: agentic-governance-prod
   ```

3. Use trace attributes (`agent.id`, `agent.name`, `query.symbol`, `audit.events_recorded`, `audit.integrity_verified`) to correlate traces with audit log entries.

## Security and access control

- Run the platform in a **controlled environment** (managed VM, container, or Kubernetes namespace) with:
  - Restricted network egress (only required endpoints).
  - Secrets managed via your standard secrets manager (not in code or logs).
- Limit write access to audit log directories to the governance service account only.
- Integrate with your existing IAM and logging/monitoring systems for:
  - Container or process restarts.
  - Disk usage and log growth.
  - Failed integrity checks or security scan findings.

## Change management and upgrades

- Pin dependency versions in `requirements.txt` and `pyproject.toml` for reproducibility.
- Test new versions in a non-production environment before upgrading:
  - Run `pytest`, `python -m ruff check .`, `python -m mypy`, and `pip-audit`.
  - Validate that existing audit logs remain readable and verifiable.
- Document any configuration or schema changes in your internal change-management system.

## Limitations

- This platform is an **observability and control layer**, not a full security boundary.
- It does not replace:
  - Network security, IAM, secrets management, or infrastructure hardening.
  - Your organization’s model risk management, third-party risk, or operational resilience frameworks.
- Always combine with human review and organizational controls before relying on outputs for high-stakes decisions.

For control objectives and mappings, see [controls.md](./controls.md). For threat model and security guidance, see [../SECURITY.md](../SECURITY.md).