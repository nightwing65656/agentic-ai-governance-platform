"""
Audit Log Entry Schema

Implements a 24-field Pydantic model for audit log entries, aligned with EU AI Act Article 12
requirements and AgentTrace's three-surface taxonomy.

References:
[1] EU AI Act Article 12: Record-Keeping Requirements. https://artificialintelligenceact.eu/article/12/
[2] AgentTrace: A Structured Logging Framework for Agent System Observability (AAAI 2026). https://arxiv.org/abs/2602.10133
"""

import hashlib
import json
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


# Enums
class SurfaceType(str, Enum):
    """AgentTrace three-surface taxonomy. [2]"""
    OPERATIONAL = "operational"
    COGNITIVE = "cognitive"
    CONTEXTUAL = "contextual"


class EventType(str, Enum):
    """Event types for audit log entries."""
    METHOD_START = "method_start"
    METHOD_COMPLETE = "method_complete"
    METHOD_ERROR = "method_error"
    LLM_PROMPT = "llm_prompt"
    LLM_COMPLETION = "llm_completion"
    TOOL_CALL = "tool_call"
    DB_QUERY = "db_query"
    HTTP_REQUEST = "http_request"
    POLICY_CHECK = "policy_check"
    HUMAN_APPROVAL = "human_approval"


class PolicyCheckResult(str, Enum):
    """Policy check results."""
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    REQUIRES_APPROVAL = "requires_approval"


class DecisionOutcome(str, Enum):
    """Decision outcomes."""
    SUCCESS = "success"
    FAILURE = "failure"
    DEFERRED = "deferred"
    ESCALATED = "escalated"
    REJECTED = "rejected"


class RetentionCategory(str, Enum):
    """Retention categories for audit logs."""
    STANDARD = "standard"
    EXTENDED = "extended"
    LEGAL_HOLD = "legal_hold"


# Sub-models
class ToolCall(BaseModel):
    """Represents a tool call within an audit log entry."""
    tool_name: str
    arguments: dict[str, str]
    result: dict[str, str] | None = None


# Main audit log entry schema
class AuditLogEntry(BaseModel):
    """
    Audit log entry schema (24 fields).

    Aligned with EU AI Act Article 12 requirements [1] and AgentTrace taxonomy. [2]
    """
    # Core identifiers
    log_id: UUID = Field(default_factory=uuid4, description="Unique identifier for this log entry.")
    trace_id: UUID = Field(..., description="Groups related events across surfaces (AgentTrace concept). [2]")
    span_id: UUID = Field(..., description="Hierarchical span within trace.")

    # Surface and event classification
    surface_type: SurfaceType = Field(..., description="One of: operational, cognitive, contextual. [2]")
    event_type: EventType = Field(..., description="Event type.")
    timestamp: datetime = Field(..., description="UTC timestamp (ISO-8601). EU AI Act Article 12 requirement. [1]")

    # Agent identification
    agent_id: str = Field(..., description="Identifier for the agent instance.")
    agent_name: str = Field(..., description="Human-readable agent name.")

    # Operational fields
    method_name: str | None = Field(None, description="For operational events.")
    duration_ms: int | None = Field(None, description="Execution duration for completed methods.")

    # LLM-specific fields
    llm_model: str | None = Field(None, description="LLM model identifier (e.g., 'gpt-4o-2024-11-20'). [1]")
    prompt_template_id: str | None = Field(None, description="Reference to prompt template (not full content). [1]")
    input_fingerprint: str | None = Field(None, description="Hash or summarization of input (not raw payload). [1]")
    output_fingerprint: str | None = Field(None, description="Hash or summarization of output.")

    # Tool calls
    tool_calls: list[ToolCall] | None = Field(None, description="List of tool calls with arguments and results.")

    # Policy and human review
    policy_check_result: PolicyCheckResult | None = Field(None, description="Policy check result.")
    human_approver_id: str | None = Field(None, description="EU AI Act: verifier identity. [1]")
    human_approval_timestamp: datetime | None = Field(None, description="When approver signed off. [1]")
    override_flag: bool = Field(False, description="Whether human overrode AI output. [1]")

    # Outcome and errors
    decision_outcome: DecisionOutcome = Field(..., description="Decision outcome.")
    error_message: str | None = Field(None, description="Error message if applicable.")

    # Model metadata
    confidence_score: float | None = Field(None, ge=0.0, le=1.0, description="Model confidence score (0.0-1.0). [1]")
    token_count: int | None = Field(None, description="Token count for cost tracking. [1]")

    # Tamper-evident hash chaining
    previous_log_hash: str = Field(..., description="SHA-256 hash of prior log entry (tamper-evident chaining). [1]")
    current_log_hash: str = Field(..., description="SHA-256 hash of this entry (computed after serialization).")

    # Retention
    retention_category: RetentionCategory = Field(..., description="Retention category.")

    @field_validator('previous_log_hash', 'current_log_hash')
    @classmethod
    def validate_hash_format(cls, v: str) -> str:
        """Validate that hash fields are valid SHA-256 hex strings (64 characters)."""
        if len(v) != 64:
            raise ValueError("Hash must be 64 characters (SHA-256 hex).")
        try:
            bytes.fromhex(v)
        except ValueError:
            raise ValueError("Hash must be valid hex string.")
        return v

    def compute_hash(self) -> str:
        """Compute SHA-256 hash of this entry (excluding current_log_hash field)."""
        # Create dict without current_log_hash
        entry_dict = self.model_dump(exclude={'current_log_hash'})
        # Serialize to JSON (sorted keys for determinism)
        json_str = json.dumps(entry_dict, sort_keys=True, default=str)
        # Compute SHA-256
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()

    def verify_hash(self) -> bool:
        """Verify that current_log_hash matches recomputation."""
        computed = self.compute_hash()
        return computed == self.current_log_hash

    @classmethod
    def create_with_hash(
        cls,
        previous_hash: str,
        **kwargs
    ) -> 'AuditLogEntry':
        """
        Create an AuditLogEntry with automatically computed current_log_hash.

        Args:
            previous_hash: SHA-256 hash of the prior log entry.
            **kwargs: Other field values.

        Returns:
            AuditLogEntry with computed current_log_hash.
        """
        # Create entry with placeholder hash
        entry = cls(previous_log_hash=previous_hash, current_log_hash="0" * 64, **kwargs)
        # Compute actual hash
        computed_hash = entry.compute_hash()
        # Update with actual hash
        entry.current_log_hash = computed_hash
        return entry
