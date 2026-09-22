"""
Unit Tests for Audit Log Schema

Tests the AuditLogEntry Pydantic model for:
- Field validation
- Hash computation
- Hash verification
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.schemas.audit_log import (
    AuditLogEntry,
    DecisionOutcome,
    EventType,
    RetentionCategory,
    SurfaceType,
)


@pytest.fixture
def sample_entry_data():
    """Sample data for creating AuditLogEntry instances."""
    return {
        "trace_id": uuid4(),
        "span_id": uuid4(),
        "surface_type": SurfaceType.OPERATIONAL,
        "event_type": EventType.METHOD_START,
        "timestamp": datetime.now(timezone.utc),
        "agent_id": "agent-001",
        "agent_name": "TestAgent",
        "decision_outcome": DecisionOutcome.SUCCESS,
        "retention_category": RetentionCategory.STANDARD,
    }


def test_create_valid_entry(sample_entry_data):
    """Test creating a valid AuditLogEntry."""
    entry = AuditLogEntry.create_with_hash(
        previous_hash="0" * 64,
        **sample_entry_data,
    )

    assert entry.log_id is not None
    assert entry.previous_log_hash == "0" * 64
    assert len(entry.current_log_hash) == 64
    assert entry.verify_hash() is True


def test_hash_chain_continuity(sample_entry_data):
    """Test that hash chain is continuous across entries."""
    entry1 = AuditLogEntry.create_with_hash(
        previous_hash="0" * 64,
        **sample_entry_data,
    )
    entry2 = AuditLogEntry.create_with_hash(
        previous_hash=entry1.current_log_hash,
        **sample_entry_data,
    )

    assert entry1.verify_hash() is True
    assert entry2.verify_hash() is True
    assert entry2.previous_log_hash == entry1.current_log_hash


def test_hash_verification_fails_on_tampering(sample_entry_data):
    """Test that hash verification fails if entry content is changed."""
    entry = AuditLogEntry.create_with_hash(
        previous_hash="0" * 64,
        **sample_entry_data,
    )

    entry.agent_name = "TamperedAgent"

    assert entry.verify_hash() is False


def test_confidence_score_validation(sample_entry_data):
    """Test that confidence_score must be between 0.0 and 1.0."""
    entry = AuditLogEntry.create_with_hash(
        previous_hash="0" * 64,
        confidence_score=0.85,
        **sample_entry_data,
    )
    assert entry.confidence_score == 0.85

    with pytest.raises(ValueError):
        AuditLogEntry.create_with_hash(
            previous_hash="0" * 64,
            confidence_score=1.5,
            **sample_entry_data,
        )

    with pytest.raises(ValueError):
        AuditLogEntry.create_with_hash(
            previous_hash="0" * 64,
            confidence_score=-0.1,
            **sample_entry_data,
        )


def test_hash_format_validation(sample_entry_data):
    """Test that hash fields must be valid SHA-256 hex strings."""
    with pytest.raises(ValueError):
        AuditLogEntry.create_with_hash(
            previous_hash="0" * 63,
            **sample_entry_data,
        )

    with pytest.raises(ValueError):
        AuditLogEntry.create_with_hash(
            previous_hash="g" * 64,
            **sample_entry_data,
        )


def test_all_surface_types(sample_entry_data):
    """Test creating entries with every allowed surface type."""
    for surface in SurfaceType:
        entry_data = {**sample_entry_data, "surface_type": surface}
        entry = AuditLogEntry.create_with_hash(
            previous_hash="0" * 64,
            **entry_data,
        )
        assert entry.surface_type == surface
        assert entry.verify_hash() is True


def test_all_event_types(sample_entry_data):
    """Test creating entries with every allowed event type."""
    for event in EventType:
        entry_data = {**sample_entry_data, "event_type": event}
        entry = AuditLogEntry.create_with_hash(
            previous_hash="0" * 64,
            **entry_data,
        )
        assert entry.event_type == event
        assert entry.verify_hash() is True
