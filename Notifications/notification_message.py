"""
=========================================================
BursaAI Notification Message
Version : 6.0 Sprint 6C
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4


@dataclass(slots=True)
class NotificationMessage:
    title: str
    body: str
    level: str = "INFO"
    event_name: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    message_id: str = field(
        default_factory=lambda: uuid4().hex[:12]
    )
    created_at: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )

    def render_text(self) -> str:
        title = str(self.title).strip()
        body = str(self.body).strip()

        if title and body:
            return f"{title}\n\n{body}"

        return title or body
