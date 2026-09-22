"""
AgentTrace-Style Instrumentation

Implements AgentTrace's three-surface taxonomy (operational, cognitive, contextual) via
decorators and context managers for easy integration with agent code.

Reference:
[1] AgentTrace: A Structured Logging Framework for Agent System Observability (AAAI 2026).
    https://arxiv.org/abs/2602.10133
"""

import time
import uuid
from collections.abc import Callable
from datetime import datetime, timezone
from functools import wraps

from src.audit.tamper_evident_logger import TamperEvidentLogger
from src.schemas.audit_log import (
    AuditLogEntry,
    DecisionOutcome,
    EventType,
    RetentionCategory,
    SurfaceType,
)

# Global logger instance (initialized on first use)
_logger: TamperEvidentLogger | None = None
_last_hash: str = "0" * 64  # Genesis hash


def get_logger() -> TamperEvidentLogger:
    """Get or initialize the global TamperEvidentLogger."""
    global _logger, _last_hash
    if _logger is None:
        _logger = TamperEvidentLogger()
        _last_hash = "0" * 64
    return _logger


def set_last_hash(hash_value: str) -> None:
    """Set the last hash for chain continuity."""
    global _last_hash
    _last_hash = hash_value


# Decorator for operational traces (method calls)
def operational_trace(event_type: EventType = EventType.METHOD_START):
    """
    Decorator to log operational traces (method calls, timing, errors).

    Usage:
        @operational_trace(EventType.METHOD_START)
        def my_method(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger()
            start_time = time.time()
            trace_id = uuid.uuid4()
            span_id = uuid.uuid4()

            try:
                # Log method_start
                entry = AuditLogEntry.create_with_hash(
                    previous_hash=_last_hash,
                    trace_id=trace_id,
                    span_id=span_id,
                    surface_type=SurfaceType.OPERATIONAL,
                    event_type=event_type,
                    timestamp=datetime.now(timezone.utc),
                    agent_id="agent-001",
                    agent_name="InstrumentedAgent",
                    method_name=func.__name__,
                    decision_outcome=DecisionOutcome.SUCCESS,
                    retention_category=RetentionCategory.STANDARD,
                )
                logger.log(entry)
                set_last_hash(entry.current_log_hash)

                # Execute function
                result = func(*args, **kwargs)

                # Log method_complete
                duration_ms = int((time.time() - start_time) * 1000)
                entry = AuditLogEntry.create_with_hash(
                    previous_hash=_last_hash,
                    trace_id=trace_id,
                    span_id=uuid.uuid4(),
                    surface_type=SurfaceType.OPERATIONAL,
                    event_type=EventType.METHOD_COMPLETE,
                    timestamp=datetime.now(timezone.utc),
                    agent_id="agent-001",
                    agent_name="InstrumentedAgent",
                    method_name=func.__name__,
                    duration_ms=duration_ms,
                    decision_outcome=DecisionOutcome.SUCCESS,
                    retention_category=RetentionCategory.STANDARD,
                )
                logger.log(entry)
                set_last_hash(entry.current_log_hash)

                return result

            except Exception as e:
                # Log method_error
                duration_ms = int((time.time() - start_time) * 1000)
                entry = AuditLogEntry.create_with_hash(
                    previous_hash=_last_hash,
                    trace_id=trace_id,
                    span_id=uuid.uuid4(),
                    surface_type=SurfaceType.OPERATIONAL,
                    event_type=EventType.METHOD_ERROR,
                    timestamp=datetime.now(timezone.utc),
                    agent_id="agent-001",
                    agent_name="InstrumentedAgent",
                    method_name=func.__name__,
                    duration_ms=duration_ms,
                    error_message=str(e),
                    decision_outcome=DecisionOutcome.FAILURE,
                    retention_category=RetentionCategory.STANDARD,
                )
                logger.log(entry)
                set_last_hash(entry.current_log_hash)
                raise

        return wrapper
    return decorator


# Decorator for cognitive traces (LLM prompts/completions)
def cognitive_trace(event_type: EventType = EventType.LLM_PROMPT):
    """
    Decorator to log cognitive traces (LLM prompts, completions, reasoning chains).

    Usage:
        @cognitive_trace(EventType.LLM_PROMPT)
        def generate_response(prompt: str):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger()
            trace_id = uuid.uuid4()
            span_id = uuid.uuid4()

            # Extract prompt (first arg or 'prompt' kwarg)
            prompt = kwargs.get('prompt', args[0] if args else None)
            input_fingerprint = f"prompt_{len(prompt) if prompt else 0}_chars" if prompt else None

            try:
                # Log llm_prompt
                entry = AuditLogEntry.create_with_hash(
                    previous_hash=_last_hash,
                    trace_id=trace_id,
                    span_id=span_id,
                    surface_type=SurfaceType.COGNITIVE,
                    event_type=event_type,
                    timestamp=datetime.now(timezone.utc),
                    agent_id="agent-001",
                    agent_name="InstrumentedAgent",
                    method_name=func.__name__,
                    input_fingerprint=input_fingerprint,
                    decision_outcome=DecisionOutcome.SUCCESS,
                    retention_category=RetentionCategory.STANDARD,
                )
                logger.log(entry)
                set_last_hash(entry.current_log_hash)

                # Execute function
                result = func(*args, **kwargs)

                # Log llm_completion
                output_fingerprint = f"response_{len(str(result)) if result else 0}_chars" if result else None
                entry = AuditLogEntry.create_with_hash(
                    previous_hash=_last_hash,
                    trace_id=trace_id,
                    span_id=uuid.uuid4(),
                    surface_type=SurfaceType.COGNITIVE,
                    event_type=EventType.LLM_COMPLETION,
                    timestamp=datetime.now(timezone.utc),
                    agent_id="agent-001",
                    agent_name="InstrumentedAgent",
                    method_name=func.__name__,
                    input_fingerprint=input_fingerprint,
                    output_fingerprint=output_fingerprint,
                    decision_outcome=DecisionOutcome.SUCCESS,
                    retention_category=RetentionCategory.STANDARD,
                )
                logger.log(entry)
                set_last_hash(entry.current_log_hash)

                return result

            except Exception as e:
                # Log error
                entry = AuditLogEntry.create_with_hash(
                    previous_hash=_last_hash,
                    trace_id=trace_id,
                    span_id=uuid.uuid4(),
                    surface_type=SurfaceType.COGNITIVE,
                    event_type=EventType.METHOD_ERROR,
                    timestamp=datetime.now(timezone.utc),
                    agent_id="agent-001",
                    agent_name="InstrumentedAgent",
                    method_name=func.__name__,
                    error_message=str(e),
                    decision_outcome=DecisionOutcome.FAILURE,
                    retention_category=RetentionCategory.STANDARD,
                )
                logger.log(entry)
                set_last_hash(entry.current_log_hash)
                raise

        return wrapper
    return decorator


# Context manager for contextual traces (HTTP, DB, cache I/O)
class contextual_trace:
    """
    Context manager to log contextual traces (HTTP, DB, cache I/O).

    Usage:
        with contextual_trace(EventType.HTTP_REQUEST, resource="https://api.example.com"):
            response = requests.get(url)
    """
    def __init__(self, event_type: EventType, resource: str | None = None):
        self.event_type = event_type
        self.resource = resource
        self.logger = get_logger()
        self.trace_id = uuid.uuid4()
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()

        # Log start event
        entry = AuditLogEntry.create_with_hash(
            previous_hash=_last_hash,
            trace_id=self.trace_id,
            span_id=uuid.uuid4(),
            surface_type=SurfaceType.CONTEXTUAL,
            event_type=self.event_type,
            timestamp=datetime.now(timezone.utc),
            agent_id="agent-001",
            agent_name="InstrumentedAgent",
            input_fingerprint=self.resource,
            decision_outcome=DecisionOutcome.SUCCESS,
            retention_category=RetentionCategory.STANDARD,
        )
        self.logger.log(entry)
        set_last_hash(entry.current_log_hash)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = int((time.time() - self.start_time) * 1000)

        if exc_type is None:
            # Log success
            entry = AuditLogEntry.create_with_hash(
                previous_hash=_last_hash,
                trace_id=self.trace_id,
                span_id=uuid.uuid4(),
                surface_type=SurfaceType.CONTEXTUAL,
                event_type=EventType.METHOD_COMPLETE,
                timestamp=datetime.now(timezone.utc),
                agent_id="agent-001",
                agent_name="InstrumentedAgent",
                duration_ms=duration_ms,
                decision_outcome=DecisionOutcome.SUCCESS,
                retention_category=RetentionCategory.STANDARD,
            )
        else:
            # Log error
            entry = AuditLogEntry.create_with_hash(
                previous_hash=_last_hash,
                trace_id=self.trace_id,
                span_id=uuid.uuid4(),
                surface_type=SurfaceType.CONTEXTUAL,
                event_type=EventType.METHOD_ERROR,
                timestamp=datetime.now(timezone.utc),
                agent_id="agent-001",
                agent_name="InstrumentedAgent",
                duration_ms=duration_ms,
                error_message=str(exc_val),
                decision_outcome=DecisionOutcome.FAILURE,
                retention_category=RetentionCategory.STANDARD,
            )

        self.logger.log(entry)
        set_last_hash(entry.current_log_hash)
        return False  # Don't suppress exceptions
