"""
=========================================================
BursaAI Event Audit Trail
Version : 6.0 Sprint 5A.4
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from Framework.event_bus import Event, EventBus


@dataclass(slots=True)
class AuditEntry:
    name: str
    source: str
    timestamp: str
    payload: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "source": self.source,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "metadata": dict(self.metadata),
        }


class EventAuditTrail:
    """
    Wildcard listener that records all framework events.
    """

    def __init__(self):
        self.entries: List[AuditEntry] = []
        self._attached_bus: EventBus | None = None

    def attach(self, event_bus: EventBus) -> None:
        if self._attached_bus is event_bus:
            return

        if self._attached_bus is not None:
            self.detach()

        self._attached_bus = event_bus
        event_bus.subscribe("*", self._handle)

    def detach(self) -> None:
        if self._attached_bus is not None:
            self._attached_bus.unsubscribe("*", self._handle)

        self._attached_bus = None

    def _handle(self, event: Event) -> None:
        self.entries.append(
            AuditEntry(
                name=event.name,
                source=event.source,
                timestamp=event.timestamp,
                payload=event.payload,
                metadata=dict(event.metadata),
            )
        )

    def names(self) -> List[str]:
        return [
            entry.name
            for entry in self.entries
        ]

    def count(self, event_name: str) -> int:
        return sum(
            1
            for entry in self.entries
            if entry.name == event_name
        )

    def clear(self) -> None:
        self.entries.clear()

    def to_list(self) -> List[Dict[str, Any]]:
        return [
            entry.to_dict()
            for entry in self.entries
        ]
