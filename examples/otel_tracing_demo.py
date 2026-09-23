"""
OpenTelemetry Tracing Demo

Demonstrates how to emit OpenTelemetry spans alongside tamper-evident audit logs.

Usage:
    # Run with no exporter (console-only)
    python -m examples.otel_tracing_demo

    # Run with OTLP export (e.g., to a local collector)
    OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 \
    OTEL_SERVICE_NAME=agentic-governance-demo \
    python -m examples.otel_tracing_demo
"""

import os
import sys
import tempfile
from pathlib import Path

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from examples.sample_agent import ResearchAgent
from src.instrumentation.agent_trace import configure_logger, get_logger


def configure_otel_tracing() -> None:
    """Configure OpenTelemetry tracing based on environment variables."""
    service_name = os.getenv("OTEL_SERVICE_NAME", "agentic-governance-demo")
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    # Always export to console for demo visibility
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    # Optionally export to an OTLP collector if configured
    if otlp_endpoint:
        exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(exporter))


def run_demo() -> None:
    """Run the demo: instrumented agent + audit logs + OpenTelemetry spans."""
    print("\n" + "=" * 60)
    print("OpenTelemetry Tracing Demo")
    print("=" * 60 + "\n")

    configure_otel_tracing()
    tracer = trace.get_tracer(__name__)

    # Use a fresh temporary log file so the hash chain starts cleanly
    log_path = tempfile.mktemp(suffix=".jsonl")
    configure_logger(log_path)

    agent = ResearchAgent()

    with tracer.start_as_current_span("agent_run") as span:
        span.set_attribute("agent.id", "agent-001")
        span.set_attribute("agent.name", "InstrumentedAgent")
        span.set_attribute("query.symbol", "AAPL")

        result = agent.run("AAPL")

        logger = get_logger()
        entries = logger.get_entries()
        integrity_verified = logger.verify_integrity()

        span.set_attribute("audit.events_recorded", len(entries))
        span.set_attribute("audit.integrity_verified", integrity_verified)

    if not entries:
        print("Demo failed: no audit events were persisted.", file=sys.stderr)
        raise SystemExit(1)

    if not integrity_verified:
        print("Demo failed: audit log integrity verification failed.", file=sys.stderr)
        raise SystemExit(1)

    print("\nAgent output:")
    print(result)
    print("\n" + "=" * 60)
    print("Demo complete.")
    print(f"Audit log: {Path(logger.log_path).resolve()}")
    print(f"Events recorded: {len(entries)}")
    print("Integrity verified: yes")
    print("OpenTelemetry spans emitted: yes")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_demo()