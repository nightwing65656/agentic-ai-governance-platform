"""
Unit Tests for Compliance Report Generator

Tests the ComplianceReportGenerator for:
- Report generation
- Summary statistics
- Disclaimer presence
"""

from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.audit.tamper_evident_logger import TamperEvidentLogger
from src.report.compliance_report import ComplianceReportGenerator
from src.schemas.audit_log import (
    AuditLogEntry,
    DecisionOutcome,
    EventType,
    RetentionCategory,
    SurfaceType,
)


@pytest.fixture(autouse=True)
def clean_files():
    """Clean up log and report files before and after each test."""
    log_path = Path("test_audit_logs.jsonl")
    report_path = Path("test_report.md")

    if log_path.exists():
        log_path.unlink()
    if report_path.exists():
        report_path.unlink()

    yield

    if log_path.exists():
        log_path.unlink()
    if report_path.exists():
        report_path.unlink()


def create_sample_entry(logger: TamperEvidentLogger, agent_name: str = "TestAgent") -> AuditLogEntry:
    """Helper to create a sample AuditLogEntry."""
    return AuditLogEntry.create_with_hash(
        previous_hash=logger.last_hash,
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


def test_report_generation():
    """Test that compliance report is generated successfully."""
    # Create log with sample entries
    logger = TamperEvidentLogger("test_audit_logs.jsonl")
    for i in range(3):
        entry = create_sample_entry(logger, f"Agent{i}")
        logger.log(entry)

    # Generate report
    generator = ComplianceReportGenerator("test_audit_logs.jsonl")
    report_path = generator.generate_report("test_report.md")

    # Verify report file exists
    assert Path(report_path).exists()

    # Verify report content
    with open(report_path, 'r') as f:
        content = f.read()

    assert "# Compliance Report" in content
    assert "Executive Summary" in content
    assert "Total events: 3" in content
    assert "Disclaimer" in content
    assert "informational and educational purposes only" in content


def test_report_summary_statistics():
    """Test that report summary statistics are correct."""
    # Create log with sample entries
    logger = TamperEvidentLogger("test_audit_logs.jsonl")
    for i in range(5):
        entry = create_sample_entry(logger, f"Agent{i}")
        logger.log(entry)

    # Generate report
    generator = ComplianceReportGenerator("test_audit_logs.jsonl")
    report_path = generator.generate_report("test_report.md")

    # Verify report content
    with open(report_path, 'r') as f:
        content = f.read()

    assert "Total events: 5" in content
    assert "Operational events: 5" in content


def test_report_disclaimer_presence():
    """Test that disclaimer is present in generated report."""
    # Create log with sample entries
    logger = TamperEvidentLogger("test_audit_logs.jsonl")
    entry = create_sample_entry(logger)
    logger.log(entry)

    # Generate report
    generator = ComplianceReportGenerator("test_audit_logs.jsonl")
    report_path = generator.generate_report("test_report.md")

    # Verify disclaimer is present
    with open(report_path, 'r') as f:
        content = f.read()

    assert "Disclaimer" in content
    assert "informational and educational purposes only" in content
    assert "DISCLAIMER.md" in content


def test_report_hash_chain_status():
    """Test that hash chain status is reported."""
    # Create log with sample entries
    logger = TamperEvidentLogger("test_audit_logs.jsonl")
    for i in range(3):
        entry = create_sample_entry(logger, f"Agent{i}")
        logger.log(entry)

    # Generate report
    generator = ComplianceReportGenerator("test_audit_logs.jsonl")
    report_path = generator.generate_report("test_report.md")

    # Verify hash chain status is reported
    with open(report_path, 'r') as f:
        content = f.read()

    assert "Tamper-Evidence Verification" in content
    assert "Hash chain status:" in content


def test_report_agent_filter():
    """Test that agent filter works correctly."""
    # Create log with mixed agents
    logger = TamperEvidentLogger("test_audit_logs.jsonl")
    for i in range(3):
        agent_name = "AgentA" if i % 2 == 0 else "AgentB"
        entry = create_sample_entry(logger, agent_name)
        logger.log(entry)

    # Generate report with filter
    generator = ComplianceReportGenerator("test_audit_logs.jsonl")
    report_path = generator.generate_report("test_report.md", agent_filter="AgentA")

    # Verify filtered content
    with open(report_path, 'r') as f:
        content = f.read()

    # Should only include AgentA entries (2 out of 3)
    assert "Total events: 2" in content


def test_empty_log_raises_error():
    """Test that generating report from empty log raises error."""
       
    # Don't log anything; the log file will be empty
    
    generator = ComplianceReportGenerator("test_audit_logs.jsonl")

    with pytest.raises(ValueError, match="No audit log entries found"):
        generator.generate_report("test_report.md")
