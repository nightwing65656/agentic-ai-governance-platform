"""
AgentTrace-Style Instrumentation

Implements AgentTrace's three-surface taxonomy (operational, cognitive, contextual)
via decorators and context managers for easy integration with agent code.
"""

import time
import uuid
from collections.abc import Callable
from datetime import datetime, timezone

from src.audit.tamper_evident_logger import TamperEvidentLogger
from src.schemas.audit_log import (
    AuditLogEntry,
    DecisionOutcome,
    EventType,
    RetentionCategory,
    SurfaceType,
)

GENESIS_HASH = "0" * 64

_logger: TamperEvidentLogger | None = None
_last_hash: str = GENESIS_HASH


def configure_logger(log_path: str | None = None) -> TamperEvidentLogger:
    """Configure a fresh logger and reset the in-memory hash-chain state."""
    global _logger, _last_hash

    _logger = TamperEvidentLogger(log_path)
    _last_hash = GENESIS_HASH
    return _logger


def get_logger() -> TamperEvidentLogger:
    """Return the configured logger, creating a default logger if necessary."""
    if _logger is None:
        return configure_logger()

    return _logger


def set_last_hash(hash_value: str) -> None:
    """Set the last hash for chain continuity."""
    global _last_hash
    _last_hash = hash_value


def operational_trace(event_type: EventType = EventType.METHOD_START):
    """Decorate a method to record start, completion, and error audit events."""

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            logger = get_logger()
            start_time = time.time()
            trace_id = uuid.uuid4()
            span_id = uuid.uuid4()

            try:
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

                result = func(*args, **kwargs)

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
            except Exception as exc:
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
                    error_message=str(exc),
                    decision_outcome=DecisionOutcome.FAILURE,
                    retention_category=RetentionCategory.STANDARD,
                )
                logger.log(entry)
                set_last_hash(entry.current_log_hash)
                raise

        return wrapper

    return decorator


def cognitive_trace(event_type: EventType = EventType.LLM_PROMPT):
    """Decorate a method to record prompt, completion, and error audit events."""

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            logger = get_logger()
            trace_id = uuid.uuid4()
            span_id = uuid.uuid4()

            prompt = kwargs.get("prompt", args[0] if args else None)
            input_fingerprint = (
                f"prompt_{len(prompt)}_chars" if prompt is not None else None
            )

            try:
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

                result = func(*args, **kwargs)

                output_fingerprint = (
                    f"response_{len(str(result))}_chars"
                    if result is not None
                    else None
                )
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
            except Exception as exc:
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
                    error_message=str(exc),
                    decision_outcome=DecisionOutcome.FAILURE,
                    retention_category=RetentionCategory.STANDARD,
                )
                logger.log(entry)
                set_last_hash(entry.current_log_hash)
                raise

        return wrapper

    return decorator


class contextual_trace:
    """Context manager that records start and completion/error audit events."""

    def __init__(self, event_type: EventType, resource: str | None = None) -> None:
        self.event_type = event_type
        self.resource = resource
        self.logger = get_logger()
        self.trace_id = uuid.uuid4()
        self.start_time: float | None = None

    def __enter__(self):
        self.start_time = time.time()

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

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self.start_time is None:
            raise RuntimeError("Contextual trace was not entered.")

        duration_ms = int((time.time() - self.start_time) * 1000)
        event_type = EventType.METHOD_COMPLETE
        decision_outcome = DecisionOutcome.SUCCESS
        error_message = None

        if exc_type is not None:
            event_type = EventType.METHOD_ERROR
            decision_outcome = DecisionOutcome.FAILURE
            error_message = str(exc_val)

        entry = AuditLogEntry.create_with_hash(
            previous_hash=_last_hash,
            trace_id=self.trace_id,
            span_id=uuid.uuid4(),
            surface_type=SurfaceType.CONTEXTUAL,
            event_type=event_type,
            timestamp=datetime.now(timezone.utc),
            agent_id="agent-001",
            agent_name="InstrumentedAgent",
            duration_ms=duration_ms,
            error_message=error_message,
            decision_outcome=decision_outcome,
            retention_category=RetentionCategory.STANDARD,
        )
        self.logger.log(entry)
        set_last_hash(entry.current_log_hash)
        return False