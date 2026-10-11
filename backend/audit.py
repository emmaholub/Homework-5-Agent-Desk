from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .models import AuditEvent


AUDIT_PATH = Path(__file__).resolve().parents[1] / "output" / "audit_trail.json"


def record(event: AuditEvent) -> None:
    """Append one redacted JSON-lines audit event; never rewrite prior events."""
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_PATH.open("a", encoding="utf-8") as handle:
        handle.write(event.model_copy(update={"timestamp": datetime.now(timezone.utc).isoformat()}).model_dump_json() + "\n")
