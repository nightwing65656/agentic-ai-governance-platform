"""
Agent Audit-Style Security Scanner

Implements Agent Audit-style pre-deployment security analysis for LLM agent applications:
- Tool-boundary detection
- Credential detection
- MCP configuration security checks

Reference:
[1] Agent Audit: A Security Analysis System for LLM Agent Applications (ACM AIES 2026).
    https://arxiv.org/abs/2603.22853
"""

import ast
import re
import uuid
from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


# Security finding severity levels
class Severity(str, Enum):
    BLOCK = "BLOCK"
    WARN = "WARN"
    INFO = "INFO"
    SUPPRESSED = "SUPP"


class SecurityFinding(BaseModel):
    """Represents a security finding from the scanner."""
    finding_id: str
    severity: Severity
    category: str
    description: str
    file_path: str
    line_number: int | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    remediation: str | None = None


class ScanReport(BaseModel):
    """Security scan report."""
    scan_id: str
    file_path: str
    findings: list[SecurityFinding]
    summary: dict[str, int]  # severity -> count


# Credential detection patterns
CREDENTIAL_PATTERNS = [
    (r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']?[a-zA-Z0-9_\-]{20,}', 'API key'),
    (r'(?i)(secret|password|passwd|pwd)\s*[=:]\s*["\']?[^\s"\']{8,}', 'Password/secret'),
    (r'(?i)(token|auth[_-]?token)\s*[=:]\s*["\']?[a-zA-Z0-9_\-]{20,}', 'Auth token'),
    (r'(?i)(private[_-]?key)\s*[=:]\s*["\']?[a-zA-Z0-9_\-]{20,}', 'Private key'),
    (r'sk_[a-zA-Z0-9]{20,}', 'OpenAI-style API key'),
    (r'ghp_[a-zA-Z0-9]{36}', 'GitHub personal access token'),
]


class AgentAuditScanner:
    """
    Agent Audit-style security scanner for LLM agent applications.

    Implements:
    - Tool-boundary detection
    - Credential detection
    - MCP configuration security checks
    """

    def __init__(self):
        self.findings: list[SecurityFinding] = []
        self.finding_counter = 0

    def scan_file(self, file_path: str) -> ScanReport:
        """
        Scan a Python file for security issues.

        Args:
            file_path: Path to the Python file.

        Returns:
            ScanReport with findings.
        """
        self.findings = []
        self.finding_counter = 0

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read file
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

        # Parse AST
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            self._add_finding(
                severity=Severity.BLOCK,
                category="syntax_error",
                description=f"Python syntax error: {e}",
                file_path=file_path,
                line_number=getattr(e, 'lineno', None),
                confidence=1.0,
                remediation="Fix syntax errors before scanning.",
            )
            return self._generate_report(file_path)

        # Run detectors
        self._detect_credentials(content, lines, file_path)
        self._detect_tool_boundaries(tree, file_path)
        self._detect_unsafe_patterns(tree, lines, file_path)

        return self._generate_report(file_path)

    def scan_config(self, config_path: str) -> ScanReport:
        """
        Scan an MCP-style YAML configuration file for security issues.

        Args:
            config_path: Path to the YAML config file.

        Returns:
            ScanReport with findings.
        """
        self.findings = []
        self.finding_counter = 0

        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        # Load YAML
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            try:
                config = yaml.safe_load(content)
            except yaml.YAMLError as e:
                self._add_finding(
                    severity=Severity.BLOCK,
                    category="yaml_syntax_error",
                    description=f"YAML syntax error: {e}",
                    file_path=config_path,
                    line_number=getattr(e, 'problem_mark', None),
                    confidence=1.0,
                    remediation="Fix YAML syntax errors before scanning.",
                )
                return self._generate_report(config_path)

        # Detect hardcoded credentials in config
        self._detect_credentials_in_config(config, config_path, lines)

        return self._generate_report(config_path)

    def _add_finding(
        self,
        severity: Severity,
        category: str,
        description: str,
        file_path: str,
        line_number: int | None = None,
        confidence: float = 1.0,
        remediation: str | None = None,
    ) -> None:
        """Add a security finding."""
        self.finding_counter += 1
        finding = SecurityFinding(
            finding_id=f"FINDING-{self.finding_counter:03d}",
            severity=severity,
            category=category,
            description=description,
            file_path=file_path,
            line_number=line_number,
            confidence=confidence,
            remediation=remediation,
        )
        self.findings.append(finding)

    def _detect_credentials(self, content: str, lines: list[str], file_path: str) -> None:
        """Detect hardcoded credentials in Python code."""
        for pattern, cred_type in CREDENTIAL_PATTERNS:
            matches = re.finditer(pattern, content)
            for match in matches:
                # Find line number
                line_num = content[:match.start()].count('\n') + 1
                self._add_finding(
                    severity=Severity.BLOCK,
                    category="hardcoded_credential",
                    description=f"Hardcoded {cred_type} detected.",
                    file_path=file_path,
                    line_number=line_num,
                    confidence=0.95,
                    remediation="Move credentials to environment variables or a secrets manager. Never commit credentials to version control.",
                )

    def _detect_tool_boundaries(self, tree: ast.AST, file_path: str) -> None:
        """Detect tool/function definitions that may require boundary checks."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and (
                'tool' in node.name.lower()
                or 'fetch' in node.name.lower()
                or 'call' in node.name.lower()
            ):
                       
                    # Check for tool-like functions
                
                    self._add_finding(
                        severity=Severity.INFO,
                        category="tool_boundary",
                        description=f"Tool-like function detected: {node.name}. Ensure proper input validation and access controls.",
                        file_path=file_path,
                        line_number=node.lineno,
                        confidence=0.7,
                        remediation="Review tool boundary: validate inputs, enforce access controls, and log all invocations.",
                    )

    def _detect_unsafe_patterns(self, tree: ast.AST, lines: list[str], file_path: str) -> None:
        """Detect unsafe patterns (e.g., eval, exec, subprocess)."""
        unsafe_calls = {'eval', 'exec', 'compile'}
        #unsafe_modules = {'subprocess', 'os.system', 'pickle'} #kept for future use

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for unsafe builtins
                if isinstance(node.func, ast.Name) and node.func.id in unsafe_calls:
                    self._add_finding(
                        severity=Severity.WARN,
                        category="unsafe_builtin",
                        description=f"Unsafe builtin '{node.func.id}' detected. This can lead to code injection vulnerabilities.",
                        file_path=file_path,
                        line_number=node.lineno,
                        confidence=0.9,
                        remediation="Avoid using eval/exec/compile with untrusted input. Use safer alternatives (e.g., ast.literal_eval for parsing literals).",
                    )

                # Check for unsafe module calls
                if ( 
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr == 'system'
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == 'os'
                ):
                                                                   
                        self._add_finding(
                            severity=Severity.WARN,
                            category="unsafe_subprocess",
                            description="os.system() detected. This can lead to command injection vulnerabilities.",
                            file_path=file_path,
                            line_number=node.lineno,
                            confidence=0.9,
                            remediation="Use subprocess.run() with shell=False and explicit argument lists instead of os.system().",
                        )

    def _detect_credentials_in_config(
        self,
        config: Any,
        file_path: str,
        lines: list[str],
    ) -> None:
        """Recursively detect hardcoded credentials in YAML dictionaries and lists."""

        credential_terms = ("key", "secret", "password", "token", "auth")

        def find_line_number(key: str, value: str) -> int | None:
            for line_number, line in enumerate(lines, start=1):
                if key in line and value in line:
                    return line_number
            return None

        def walk(value: Any, path: str = "") -> None:
            if isinstance(value, dict):
                for key, nested_value in value.items():
                    current_path = f"{path}.{key}" if path else str(key)

                    if isinstance(nested_value, (dict, list)):
                        walk(nested_value, current_path)
                    elif isinstance(nested_value, str):
                        key_text = str(key).lower()
                        if (
                            any(term in key_text for term in credential_terms)
                            and len(nested_value) > 8
                            and not nested_value.startswith("${")
                        ):
                            self._add_finding(
                                severity=Severity.BLOCK,
                                category="hardcoded_credential_config",
                                description=(
                                    f"Hardcoded credential in config at "
                                    f"'{current_path}'."
                                ),
                                file_path=file_path,
                                line_number=find_line_number(
                                    str(key), nested_value
                                ),
                                confidence=0.9,
                                remediation=(
                                    "Use environment-variable references such as "
                                    "'${API_KEY}' or a dedicated secrets manager."
                                ),
                            )
            elif isinstance(value, list):
                for index, nested_value in enumerate(value):
                    walk(nested_value, f"{path}[{index}]")

        walk(config)

    def _generate_report(self, file_path: str) -> ScanReport:
        """Generate scan report."""
        summary = {
            "BLOCK": sum(1 for f in self.findings if f.severity == Severity.BLOCK),
            "WARN": sum(1 for f in self.findings if f.severity == Severity.WARN),
            "INFO": sum(1 for f in self.findings if f.severity == Severity.INFO),
            "SUPPRESSED": sum(1 for f in self.findings if f.severity == Severity.SUPPRESSED),
        }
        return ScanReport(
            scan_id=f"SCAN-{uuid.uuid4().hex[:8]}",
            file_path=file_path,
            findings=self.findings,
            summary=summary,
        )


# CLI entry point
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m src.security.agent_audit <file_or_config_path>")
        sys.exit(1)

    target_path = sys.argv[1]
    scanner = AgentAuditScanner()

    if target_path.endswith(('.yaml', '.yml')):
        report = scanner.scan_config(target_path)
    else:
        report = scanner.scan_file(target_path)

    # Print report
    print(f"\n{'='*60}")
    print(f"Security Scan Report: {report.scan_id}")
    print(f"Target: {report.file_path}")
    print(f"{'='*60}")
    print("\nSummary:")
    print(f"  BLOCK: {report.summary['BLOCK']}")
    print(f"  WARN:  {report.summary['WARN']}")
    print(f"  INFO:  {report.summary['INFO']}")
    print("\nFindings:")
    if not report.findings:
        print("  No findings.")
    else:
        for finding in report.findings:
            print(f"\n  [{finding.severity}] {finding.finding_id}: {finding.category}")
            print(f"    {finding.description}")
            if finding.line_number:
                print(f"    Location: {finding.file_path}:{finding.line_number}")
            if finding.remediation:
                print(f"    Remediation: {finding.remediation}")
    print(f"\n{'='*60}\n")
