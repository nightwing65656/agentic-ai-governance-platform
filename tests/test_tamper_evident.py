"""Unit tests for the tamper-evident audit logger."""

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.audit.tamper_evident_logger import TamperEvidentLogger
from src.schemas.audit_log import (
    AuditLogEntry,
    DecisionOutcome,
    EventType,
    RetentionCategory,
    SurfaceType,
)


def create_sample_entry(
    previous_hash: str, agent_name: str = "TestAgent"
) -> AuditLogEntry:
    """Create a deterministic sample audit entry."""
    return AuditLogEntry.create_with_hash(
        previous_hash=previous_hash,
        trace_id="00000000-0000-0000-0000-000000000001",
        span_id="00000000-0000-0000-0000-000000000002",
        surface_type=SurfaceType.OPERATIONAL,
        event_type=EventType.METHOD_START,
        timestamp=datetime.now(timezone.utc),
        agent_id="agent-001",
        agent_name=agent_name,
        decision_outcome=DecisionOutcome.SUCCESS,
        retention_category=RetentionCategory.STANDARD,
    )


def test_logger_creates_file(tmp_path: Path) -> None:
    """The logger creates its JSONL file when initialized."""
    log_path = tmp_path / "audit.jsonl"

    logger = TamperEvidentLogger(str(log_path))
    entry = create_sample_entry(logger.last_hash)
    logger.log(entry)

    assert log_path.exists()


def test_hash_chain_continuity(tmp_path: Path) -> None:
    """Multiple entries form a continuous hash chain."""
    log_path = tmp_path / "audit.jsonl"
    logger = TamperEvidentLogger(str(log_path))

    entry1 = create_sample_entry(logger.last_hash, "Agent1")
    logger.log(entry1)

    entry2 = create_sample_entry(logger.last_hash, "Agent2")
    logger.log(entry2)

    entry3 = create_sample_entry(logger.last_hash, "Agent3")
    logger.log(entry3)

    entries = logger.get_entries()

    assert len(entries) == 3
    assert entries[0].previous_log_hash == "0" * 64
    assert entries[1].previous_log_hash == entries[0].current_log_hash
    assert entries[2].previous_log_hash == entries[1].current_log_hash


def test_integrity_verification(tmp_path: Path) -> None:
    """A valid log passes integrity verification."""
    log_path = tmp_path / "audit.jsonl"
    logger = TamperEvidentLogger(str(log_path))

    for index in range(5):
        entry = create_sample_entry(logger.last_hash, f"Agent{index}")
        logger.log(entry)

    assert logger.verify_integrity() is True


def test_tamper_detection(tmp_path: Path) -> None:
    """Changing persisted data causes integrity verification to fail."""
    log_path = tmp_path / "audit.jsonl"
    logger = TamperEvidentLogger(str(log_path))

    entry1 = create_sample_entry(logger.last_hash, "Agent1")
    logger.log(entry1)

    entry2 = create_sample_entry(logger.last_hash, "Agent2")
    logger.log(entry2)

    lines = log_path.read_text(encoding="utf-8").splitlines()
    entry2_data = json.loads(lines[1])
    entry2_data["agent_name"] = "TamperedAgent"
    lines[1] = json.dumps(entry2_data)

    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    assert logger.verify_integrity() is False


def test_get_last_entry(tmp_path: Path) -> None:
    """The logger returns the final persisted audit entry."""
    log_path = tmp_path / "audit.jsonl"
    logger = TamperEvidentLogger(str(log_path))

    for index in range(3):
        entry = create_sample_entry(logger.last_hash, f"Agent{index}")
        logger.log(entry)

    last_entry = logger.get_last_entry()

    assert last_entry is not None
    assert last_entry.agent_name == "Agent2"


def test_empty_log_verification(tmp_path: Path) -> None:
    """An empty log is valid."""
    logger = TamperEvidentLogger(str(tmp_path / "audit.jsonl"))

    assert logger.verify_integrity() is True


def test_reopened_logger_restores_last_hash_and_appends(tmp_path: Path) -> None:
    """A new logger instance resumes a valid existing hash chain."""
    log_path = tmp_path / "audit.jsonl"

    first_logger = TamperEvidentLogger(str(log_path))
    first_entry = create_sample_entry(first_logger.last_hash, "FirstRun")
    first_logger.log(first_entry)

    reopened_logger = TamperEvidentLogger(str(log_path))

    assert reopened_logger.last_hash == first_entry.current_log_hash

    second_entry = create_sample_entry(reopened_logger.last_hash, "SecondRun")
    reopened_logger.log(second_entry)

    entries = reopened_logger.get_entries()
    assert len(entries) == 2
    assert entries[1].previous_log_hash == entries[0].current_log_hash
    assert reopened_logger.verify_integrity() is True


def test_reopened_logger_rejects_tampered_log(tmp_path: Path) -> None:
    """A logger refuses to reopen a log whose integrity has failed."""
    log_path = tmp_path / "audit.jsonl"

    logger = TamperEvidentLogger(str(log_path))
    entry = create_sample_entry(logger.last_hash)
    logger.log(entry)

    lines = log_path.read_text(encoding="utf-8").splitlines()
    entry_data = json.loads(lines[0])
    entry_data["agent_name"] = "TamperedAgent"
    log_path.write_text(json.dumps(entry_data) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="integrity"):
        TamperEvidentLogger(str(log_path))
