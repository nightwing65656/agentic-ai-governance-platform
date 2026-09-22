# Compliance Report (Sample)

**Generated:** 2026-09-22 10:35:00 UTC  
**Report ID:** report-001  
**Agent:** ResearchAgent (agent-001)  
**Log Source:** examples/sample_audit_log.jsonl  

---

## Executive Summary

This report summarizes the execution of the `ResearchAgent` based on audit logs captured between `2026-09-22T10:30:00Z` and `2026-09-22T10:30:02Z`.

**Key metrics:**
- Total events: 3
- Operational events: 2
- Cognitive events: 1
- Contextual events: 0
- Policy violations: 0
- Human approvals required: 0
- Human approvals granted: 0

**Overall status:** ✅ No policy violations detected.

---

## Event Timeline

| Timestamp (UTC) | Event Type | Surface | Method/Tool | Outcome |
|---|---|---|---|---|
| 2026-09-22T10:30:00Z | method_start | operational | run | success |
| 2026-09-22T10:30:01Z | tool_call | operational | fetch_market_data | success |
| 2026-09-22T10:30:02Z | method_complete | cognitive | run | success |

---

## Policy Compliance

### Policy: no_pii_without_approval

**Status:** Not triggered (no PII detected in inputs).

### Policy: no_trade_execution_without_signoff

**Status:** Not triggered (no trade execution actions).

---

## Human Review

**Human approvals required:** 0  
**Human approvals granted:** 0  
**Overrides:** 0  

No human review was required for this execution.

---

## Data Provenance

**Agent ID:** agent-001  
**Agent Name:** ResearchAgent  
**Trace ID:** 6ba7b810-9dad-11d1-80b4-00c04fd430c8  

All events are traceable to the original agent execution via the `trace_id` and `span_id` fields.

---

## Tamper-Evidence Verification

**Hash chain status:** ✅ Verified (all `current_log_hash` values match recomputation).

No tampering detected in the audit log.

---

## Disclaimer

**This report is for informational and educational purposes only.** It does not constitute compliance certification, legal advice, or regulatory approval. All outputs must be reviewed by a qualified human before any use in production, regulatory submission, or decision-making contexts.

See [DISCLAIMER.md](../DISCLAIMER.md) for full terms.

---

**End of Report**
