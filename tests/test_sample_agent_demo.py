"""Tests for the instrumented sample-agent workflow."""

from pathlib import Path

from examples.sample_agent import ResearchAgent
from src.instrumentation.agent_trace import configure_logger
from src.schemas.audit_log import EventType, SurfaceType


def test_sample_agent_run_creates_valid_operational_audit_log(tmp_path: Path) -> None:
    """The sample agent emits a valid start/completion audit trace."""
    log_path = tmp_path / "sample_agent_audit.jsonl"
    logger = configure_logger(str(log_path))

    result = ResearchAgent().run("AAPL")

    assert "Symbol: AAPL" in result
    assert log_path.exists()

    entries = logger.get_entries()
    assert len(entries) == 2
    assert [entry.event_type for entry in entries] == [
        EventType.METHOD_START,
        EventType.METHOD_COMPLETE,
    ]
    assert all(entry.surface_type == SurfaceType.OPERATIONAL for entry in entries)
    assert entries[1].previous_log_hash == entries[0].current_log_hash
    assert logger.verify_integrity() is True