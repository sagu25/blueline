"""
STEWARD — Immutable Audit Log Agent
Production: writes to Azure Blob Storage (immutable, append-only).
POC: generates and displays the structured audit log entry.
"""

from datetime import datetime, timezone
import uuid


def create_audit_entry(
    pipeline: str,
    finding_summary: str,
    classification: str,
    confidence: float,
    action_taken: str,
    agents_involved: list[str],
    human_gate_required: bool = True,
) -> dict:
    return {
        "run_id":               f"BL-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8].upper()}",
        "timestamp_utc":        datetime.now(timezone.utc).isoformat(),
        "pipeline":             pipeline,
        "agents_involved":      agents_involved,
        "finding_summary":      finding_summary[:300],
        "classification":       classification,
        "confidence_score":     round(confidence, 2),
        "action_taken":         action_taken,
        "human_gate_required":  human_gate_required,
        "human_gate_status":    "PENDING_APPROVAL" if human_gate_required else "NOT_REQUIRED",
        "immutable":            True,
        "storage_target":       "Azure Blob Storage — blueline-audit container (POC: display only)",
        "retention_policy":     "7 years (compliance)",
    }
