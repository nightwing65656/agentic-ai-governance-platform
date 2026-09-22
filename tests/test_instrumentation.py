"""
Unit Tests for AgentTrace-Style Instrumentation

Tests the operational_trace, cognitive_trace, and contextual_trace decorators/context managers.
"""

from pathlib import Path

import pytest

from src.instrumentation.agent_trace import (
    cognitive_trace,
    contextual_trace,
    get_logger,
    operational_trace,
)
from src.schemas.audit_log import (
    EventType,
    SurfaceType,
)


@pytest.fixture(autouse=True)
def clean_audit_log():
    """Clean up audit log before and after each test."""
    log_path = Path("audit_logs.jsonl")
    if log_path.exists():
        log_path.unlink()
    yield
    if log_path.exists():
        log_path.unlink()


def test_operational_trace_decorator():
    """Test that operational_trace decorator logs method calls."""
    @operational_trace(EventType.METHOD_START)
    def test_function(x: int) -> int:
        return x * 2

    result = test_function(5)
    assert result == 10

    # Verify log file was created
    log_path = Path("audit_logs.jsonl")
    assert log_path.exists()

    # Verify entries were logged
    logger = get_logger()
    entries = logger.get_entries()
    assert len(entries) >= 2  # At least method_start and method_complete

    # Verify surface type
    assert all(e.surface_type == SurfaceType.OPERATIONAL for e in entries)


def test_cognitive_trace_decorator():
    """Test that cognitive_trace decorator logs LLM-like calls."""
    @cognitive_trace(EventType.LLM_PROMPT)
    def generate_response(prompt: str) -> str:
        return f"Response to: {prompt}"

    result = generate_response("Hello")
    assert "Hello" in result

    # Verify log file was created
    log_path = Path("audit_logs.jsonl")
    assert log_path.exists()

    # Verify entries were logged
    logger = get_logger()
    entries = logger.get_entries()
    assert len(entries) >= 2  # At least llm_prompt and llm_completion

    # Verify surface type
    assert all(e.surface_type == SurfaceType.COGNITIVE for e in entries)

    # Verify fingerprints were set
    assert any(e.input_fingerprint is not None for e in entries)
    assert any(e.output_fingerprint is not None for e in entries)


def test_contextual_trace_context_manager():
    """Test that contextual_trace context manager logs I/O operations."""
    with contextual_trace(EventType.HTTP_REQUEST, resource="https://api.example.com"):
        # Simulate HTTP request
        pass

    # Verify log file was created
    log_path = Path("audit_logs.jsonl")
    assert log_path.exists()

    # Verify entries were logged
    logger = get_logger()
    entries = logger.get_entries()
    assert len(entries) >= 2  # At least start and complete

    # Verify surface type
    assert all(e.surface_type == SurfaceType.CONTEXTUAL for e in entries)

    # Verify resource was logged
    assert any(e.input_fingerprint == "https://api.example.com" for e in entries)


def test_error_logging_in_operational_trace():
    """Test that errors are logged correctly."""
    @operational_trace(EventType.METHOD_START)
    def failing_function():
        raise ValueError("Test error")

    with pytest.raises(ValueError):
        failing_function()

    # Verify log file was created
    log_path = Path("audit_logs.jsonl")
    assert log_path.exists()

    # Verify error entry was logged
    logger = get_logger()
    entries = logger.get_entries()
    assert any(e.event_type == EventType.METHOD_ERROR for e in entries)
    assert any(e.error_message == "Test error" for e in entries)


def test_hash_chain_continuity_across_decorators():
    """Test that hash chain is continuous across multiple decorated functions."""
    @operational_trace(EventType.METHOD_START)
    def function_a():
        return "A"

    @cognitive_trace(EventType.LLM_PROMPT)
    def function_b(prompt: str):
        return f"Response: {prompt}"

    # Call both functions
    function_a()
    function_b("Hello")

    # Verify hash chain is continuous
    logger = get_logger()
    entries = logger.get_entries()
    assert len(entries) >= 4

    # Verify each entry's previous_hash matches the prior entry's current_hash
    for i in range(1, len(entries)):
        assert entries[i].previous_log_hash == entries[i-1].current_log_hash
