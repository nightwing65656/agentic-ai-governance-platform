# Minimal Dockerfile for Agentic AI Governance & Observability Platform
# Intended for pilot / evaluation deployments, not hardened production use.

FROM python:3.11-slim

WORKDIR /app

# Install system deps needed for building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install project with dev extras (includes pytest, ruff, mypy, pip-audit, OTLP exporter)
RUN pip install --no-cache-dir ".[dev]"

# Default command: run demo + security scan on sample agent
# Override in docker-compose or via `docker run` as needed.
CMD ["sh", "-c", "agent-governance --demo && agent-governance --scan examples/sample_agent.py"]