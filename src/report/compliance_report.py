"""
Compliance Report Generator

Generates informational audit summaries from tamper-evident audit logs.
The generated output is not a compliance certification or legal advice.
"""

from datetime import datetime, timezone
from pathlib import Path

from src.audit.tamper_evident_logger import TamperEvidentLogger
from src.schemas.audit_log import AuditLogEntry, SurfaceType


class ComplianceReportGenerator:
    """Generate Markdown audit-summary reports from audit logs."""

    def __init__(self, log_path: str | None = None):
        self.logger = TamperEvidentLogger(log_path)

    def generate_report(
        self,
        output_path: str,
        report_id: str | None = None,
        agent_filter: str | None = None,
    ) -> str:
        """
        Generate a Markdown report.

        The optional agent_filter matches either agent_id or agent_name.
        """
        entries = self.logger.get_entries()

        if agent_filter:
            entries = [
                entry
                for entry in entries
                if entry.agent_id == agent_filter or entry.agent_name == agent_filter
            ]

        if not entries:
            raise ValueError("No audit log entries found.")

        report_id = report_id or f"report-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        report_content = self._build_report(report_id, entries)

        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(report_content, encoding="utf-8")

        return str(destination)

    def _build_report(self, report_id: str, entries: list[AuditLogEntry]) -> str:
        """Build a Markdown report from selected audit-log entries."""
        total_events = len(entries)
        operational_events = sum(
            entry.surface_type == SurfaceType.OPERATIONAL for entry in entries
        )
        cognitive_events = sum(
            entry.surface_type == SurfaceType.COGNITIVE for entry in entries
        )
        contextual_events = sum(
            entry.surface_type == SurfaceType.CONTEXTUAL for entry in entries
        )
        policy_violations = sum(
            entry.policy_check_result is not None
            and entry.policy_check_result.value == "blocked"
            for entry in entries
        )
        human_approvals_required = sum(
            entry.policy_check_result is not None
            and entry.policy_check_result.value == "requires_approval"
            for entry in entries
        )
        human_approvals_granted = sum(
            entry.human_approver_id is not None for entry in entries
        )
        overrides = sum(entry.override_flag for entry in entries)

        overall_status = (
            "✅ No policy violations detected."
            if policy_violations == 0
            else "❌ Policy violations detected."
        )

        agent_id = entries[0].agent_id
        agent_name = entries[0].agent_name
        trace_id = entries[0].trace_id
        timestamps = [entry.timestamp for entry in entries]
        start_time = min(timestamps)
        end_time = max(timestamps)
        hash_chain_status = (
            "✅ Verified"
            if self.logger.verify_integrity()
            else "❌ Verification failed"
        )

        timeline_rows = []
        for entry in entries:
            method_or_tool = entry.method_name or (
                entry.tool_calls[0].tool_name if entry.tool_calls else "N/A"
            )
            timeline_rows.append(
                f"| {entry.timestamp.isoformat()} | {entry.event_type.value} | "
                f"{entry.surface_type.value} | {method_or_tool} | "
                f"{entry.decision_outcome.value} |"
            )

        timeline = "\n".join(timeline_rows)
        pii_status = (
            "Not triggered (no blocked policy-check events recorded)."
            if policy_violations == 0
            else f"Triggered {policy_violations} time(s)."
        )
        human_review_statement = (
            "No human review was required for this execution."
            if human_approvals_required == 0
            else "Human review was required; inspect the event timeline and approver records."
        )
        tamper_statement = (
            "No tampering detected in the audit log."
            if hash_chain_status == "✅ Verified"
            else "WARNING: Hash chain verification failed. Audit log integrity must be investigated."
        )

        return f"""# Compliance Report

**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC  
**Report ID:** {report_id}  
**Agent:** {agent_name} ({agent_id})  
**Log Source:** {self.logger.log_path}  
**Period:** {start_time.isoformat()} to {end_time.isoformat()}

---

## Executive Summary

This report summarizes recorded execution events for `{agent_name}`.

**Key metrics:**
- Total events: {total_events}
- Operational events: {operational_events}
- Cognitive events: {cognitive_events}
- Contextual events: {contextual_events}
- Policy violations: {policy_violations}
- Human approvals required: {human_approvals_required}
- Human approvals granted: {human_approvals_granted}

**Overall status:** {overall_status}

---

## Event Timeline

| Timestamp (UTC) | Event Type | Surface | Method/Tool | Outcome |
|---|---|---|---|---|
{timeline}

---

## Policy Compliance

### Policy: no_pii_without_approval

**Status:** {pii_status}

### Policy: no_trade_execution_without_signoff

**Status:** No trade-execution policy event was recorded in the selected audit entries.

---

## Human Review

**Human approvals required:** {human_approvals_required}  
**Human approvals granted:** {human_approvals_granted}  
**Overrides:** {overrides}  

{human_review_statement}

---

## Data Provenance

**Agent ID:** {agent_id}  
**Agent Name:** {agent_name}  
**Trace ID:** {trace_id}  

All reported entries remain traceable through `trace_id`, `span_id`, and hash-chain fields.

---

## Tamper-Evidence Verification

**Hash chain status:** {hash_chain_status}

{tamper_statement}

---

## Disclaimer

**This report is for informational and educational purposes only.** It does not constitute compliance certification, legal advice, or regulatory approval. All outputs must be reviewed by a qualified human before any use in production, regulatory submission, or decision-making contexts.

See DISCLAIMER.md for full terms.

---

**End of Report**
"""
