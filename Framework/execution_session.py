"""
=========================================================
BursaAI Execution Session
Version : 6.0 Sprint 6A
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


@dataclass(slots=True)
class ExecutionSession:
    run_id: str = field(
        default_factory=lambda: uuid4().hex[:12]
    )
    pipeline_version: str = "6.0"
    started_at: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )
    completed_at: Optional[str] = None
    duration_ms: float = 0.0
    symbols: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def complete(self, duration_ms: float) -> None:
        self.duration_ms = max(float(duration_ms), 0.0)
        self.completed_at = datetime.now(
            timezone.utc
        ).isoformat()
