"""
CLI Entry Point

Command-line interface for running demos, security scans, and generating compliance reports.

Usage:
    python -m src.main --demo
    python -m src.main --scan <file_or_config_path>
    python -m src.main --generate-report --input <log_path> --output <report_path>
"""

import argparse
import sys


def run_demo():
    """Run instrumentation demo with sample agent."""
    print("\n" + "="*60)
    print("Running Instrumentation Demo")
    print("="*60 + "\n")

    # Import sample agent
    from examples.sample_agent import ResearchAgent

    # Run agent
    agent = ResearchAgent()
    result = agent.run("AAPL")

    print("Agent output:")
    print(result)
    print("\n" + "="*60)
    print("Demo complete. Check audit_logs.jsonl for logged events.")
    print("="*60 + "\n")


def run_scan(target_path: str):
    """Run security scan on a file or config."""
    from src.security.agent_audit import AgentAuditScanner

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


def generate_report(input_path: str, output_path: str):
    """Generate compliance report from audit log."""
    from src.report.compliance_report import ComplianceReportGenerator

    generator = ComplianceReportGenerator(log_path=input_path)
    report_path = generator.generate_report(output_path)

    print(f"\n{'='*60}")
    print("Compliance Report Generated")
    print(f"{'='*60}")
    print(f"Input: {input_path}")
    print(f"Output: {report_path}")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Agentic AI Governance & Observability Platform CLI")

    parser.add_argument('--demo', action='store_true', help='Run instrumentation demo with sample agent.')
    parser.add_argument('--scan', type=str, metavar='PATH', help='Run security scan on a file or config.')
    parser.add_argument('--generate-report', action='store_true', help='Generate compliance report from audit log.')
    parser.add_argument('--input', type=str, help='Input log path (for --generate-report).')
    parser.add_argument('--output', type=str, help='Output report path (for --generate-report).')

    args = parser.parse_args()

    if args.demo:
        run_demo()
    elif args.scan:
        run_scan(args.scan)
    elif args.generate_report:
        if not args.input or not args.output:
            print("Error: --input and --output are required for --generate-report.")
            sys.exit(1)
        generate_report(args.input, args.output)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
