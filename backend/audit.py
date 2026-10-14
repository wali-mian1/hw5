"""Append-only audit trail for agent runs and MCP tool calls."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any


class AuditTrail:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = Lock()

    def append(self, event: dict[str, Any]) -> None:
        """Append one event without deleting events from earlier runs."""
        with self._lock:
            if self.path.exists():
                existing = json.loads(self.path.read_text())
                if not isinstance(existing, list):
                    raise ValueError("Audit trail must contain a JSON list")
            else:
                existing = []
            existing.append(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    **event,
                }
            )
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(existing, indent=2) + "\n")
