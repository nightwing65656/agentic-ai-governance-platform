"""
Unit Tests for Tamper-Evident Logger

Tests the TamperEvidentLogger for:
- Hash chain integrity
- Tamper detection
- Log verification
"""

import os
import tempfile
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


@pytest.fixture(autouse=True)
def clean_audit_log():
    """Clean up audit log before and after each test."""
    log_path = Path("test_audit_logs.jsonl")
    if log_path.exists():
        log_path.unlink()
    yield
    if log_path.exists():
        log_path.unlink()


def create_sample_entry(previous_hash: str, agent_name: str = "TestAgent") -> AuditLogEntry:
    """Helper to create a sample AuditLogEntry."""
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


def test_logger_creates_file():
    """Test that logger creates log file on first write."""
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
        temp_path = f.name

    try:
        logger = TamperEvidentLogger(temp_path)
        entry = create_sample_entry(logger.last_hash)
        logger.log(entry)

        assert Path(temp_path).exists()
    finally:
        os.unlink(temp_path)


def test_hash_chain_continuity():
    """Test that hash chain is continuous across multiple entries."""
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
        temp_path = f.name

    try:
        logger = TamperEvidentLogger(temp_path)

        # Log multiple entries
        entry1 = create_sample_entry(logger.last_hash, "Agent1")
        logger.log(entry1)

        entry2 = create_sample_entry(logger.last_hash, "Agent2")
        logger.log(entry2)

        entry3 = create_sample_entry(logger.last_hash, "Agent3")
        logger.log(entry3)

        # Verify all entries are in log
        entries = logger.get_entries()
        assert len(entries) == 3

        # Verify hash chain continuity
        assert entries[0].previous_log_hash == "0" * 64
        assert entries[1].previous_log_hash == entries[0].current_log_hash
        assert entries[2].previous_log_hash == entries[1].current_log_hash
    finally:
        os.unlink(temp_path)


def test_integrity_verification():
    """Test that integrity verification passes for valid logs."""
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
        temp_path = f.name

    try:
        logger = TamperEvidentLogger(temp_path)

        # Log multiple entries
        for i in range(5):
            entry = create_sample_entry(logger.last_hash, f"Agent{i}")
            logger.log(entry)

        # Verify integrity
        assert logger.verify_integrity() is True
    finally:
        os.unlink(temp_path)


def test_tamper_detection():
    """Test that tampering is detected."""
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False, mode='w') as f:
        temp_path = f.name

    try:
        logger = TamperEvidentLogger(temp_path)

        # Log entries
        entry1 = create_sample_entry(logger.last_hash, "Agent1")
        logger.log(entry1)

        entry2 = create_sample_entry(logger.last_hash, "Agent2")
        logger.log(entry2)

        # Tamper with the file (modify agent_name in second entry)
        with open(temp_path, 'r') as file:
            lines = file.readlines()

        # Modify second line (change agent_name)
        import json
        entry2_dict = json.loads(lines[1])
        entry2_dict['agent_name'] = "TamperedAgent"
        lines[1] = json.dumps(entry2_dict) + '\n'

        with open(temp_path, 'w') as file:
            file.writelines(lines)

        # Verify integrity should fail
        assert logger.verify_integrity() is False
    finally:
        os.unlink(temp_path)


def test_get_last_entry():
    """Test getting the last entry from log."""
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
        temp_path = f.name

    try:
        logger = TamperEvidentLogger(temp_path)

        # Log entries
        for i in range(3):
            entry = create_sample_entry(logger.last_hash, f"Agent{i}")
            logger.log(entry)

        # Get last entry
        last_entry = logger.get_last_entry()
        assert last_entry is not None
        assert last_entry.agent_name == "Agent2"
    finally:
        os.unlink(temp_path)


def test_empty_log_verification():
    """Test that empty log passes verification."""
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
        temp_path = f.name

    try:
        logger = TamperEvidentLogger(temp_path)

        # Don't log anything
        assert logger.verify_integrity() is True
    finally:
        os.unlink(temp_path)
