"""
Unit Tests for Agent Audit-Style Security Scanner

Tests the AgentAuditScanner for:
- Credential detection
- Tool-boundary detection
- Unsafe pattern detection
- Config scanning
"""

import os
import tempfile

import pytest

from src.security.agent_audit import (
    AgentAuditScanner,
)


@pytest.fixture
def sample_python_file():
    """Create a temporary Python file with security issues."""
    content = """
# Sample Python file with security issues

API_KEY = "test_api_key_nightwing1123581321345589144"  # Hardcoded credential

def fetch_data(tool_input: str):
    return eval(tool_input)  # Unsafe builtin

def call_external_service():
    import os
    os.system("ls -la")  # Unsafe subprocess
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(content)
        temp_path = f.name

    yield temp_path

    # Cleanup
    os.unlink(temp_path)


@pytest.fixture
def sample_config_file():
    """Create a temporary YAML config file with security issues."""
    content = """
version: "1.0"
agent_name: "TestAgent"

tools:
  - name: fetch_data
    endpoint: "https://api.example.com"
    auth:
      type: "bearer"
      token: "hardcoded_token_123456789012345678"

policies:
  - name: "no_pii"
    condition: "data_contains_pii == true"
    action: "require_human_approval"
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(content)
        temp_path = f.name

    yield temp_path

    # Cleanup
    os.unlink(temp_path)


def test_credential_detection(sample_python_file):
    """Test that hardcoded credentials are detected."""
    scanner = AgentAuditScanner()
    report = scanner.scan_file(sample_python_file)

    # Should detect hardcoded API key
    assert any(f.category == "hardcoded_credential" for f in report.findings)
    assert report.summary["BLOCK"] >= 1


def test_unsafe_builtin_detection(sample_python_file):
    """Test that unsafe builtins (eval) are detected."""
    scanner = AgentAuditScanner()
    report = scanner.scan_file(sample_python_file)

    # Should detect eval usage
    assert any(f.category == "unsafe_builtin" for f in report.findings)
    assert report.summary["WARN"] >= 1


def test_unsafe_subprocess_detection(sample_python_file):
    """Test that unsafe subprocess (os.system) is detected."""
    scanner = AgentAuditScanner()
    report = scanner.scan_file(sample_python_file)

    # Should detect os.system usage
    assert any(f.category == "unsafe_subprocess" for f in report.findings)
    assert report.summary["WARN"] >= 1


def test_tool_boundary_detection(sample_python_file):
    """Test that tool-like functions are detected."""
    scanner = AgentAuditScanner()
    report = scanner.scan_file(sample_python_file)

    # Should detect tool-like functions (fetch_data, call_external_service)
    assert any(f.category == "tool_boundary" for f in report.findings)
    assert report.summary["INFO"] >= 1


def test_config_credential_detection(sample_config_file):
    """Test that hardcoded credentials in YAML config are detected."""
    scanner = AgentAuditScanner()
    report = scanner.scan_config(sample_config_file)

    # Should detect hardcoded token in config
    assert any(f.category == "hardcoded_credential_config" for f in report.findings)
    assert report.summary["BLOCK"] >= 1


def test_clean_file_no_findings():
    """Test that a clean file produces no findings."""
    content = """
# Clean Python file with no security issues

def add(a: int, b: int) -> int:
    return a + b
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(content)
        temp_path = f.name

    try:
        scanner = AgentAuditScanner()
        report = scanner.scan_file(temp_path)

        # Should have no BLOCK or WARN findings
        assert report.summary["BLOCK"] == 0
        assert report.summary["WARN"] == 0
    finally:
        os.unlink(temp_path)


def test_file_not_found():
    """Test that FileNotFoundError is raised for missing files."""
    scanner = AgentAuditScanner()

    with pytest.raises(FileNotFoundError):
        scanner.scan_file("nonexistent_file.py")


def test_scan_report_structure(sample_python_file):
    """Test that scan report has correct structure."""
    scanner = AgentAuditScanner()
    report = scanner.scan_file(sample_python_file)

    assert report.scan_id is not None
    assert report.file_path == sample_python_file
    assert isinstance(report.findings, list)
    assert isinstance(report.summary, dict)
    assert "BLOCK" in report.summary
    assert "WARN" in report.summary
    assert "INFO" in report.summary
