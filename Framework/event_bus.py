"""
=========================================================
BursaAI Event Bus
Version : 6.0 Sprint 5A.0
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional


@dataclass(slots=True)
class Event:
    name: str
    payload: Any = None
    source: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )
    metadata: Dict[str, Any] = field(default_factory=dict)


EventHandler = Callable[[Event], None]


class EventBus:
    """
    In-process synchronous event bus.
    """

    def __init__(self):
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._wildcard_handlers: List[EventHandler] = []
        self.history: List[Event] = []

    def subscribe(
        self,
        event_name: str,
        handler: EventHandler,
    ) -> None:
        if not callable(handler):
            raise TypeError("Event handler must be callable.")

        key = str(event_name).strip()

        if key == "*":
            if handler not in self._wildcard_handlers:
                self._wildcard_handlers.append(handler)
            return

        self._handlers.setdefault(
            key,
            [],
        )

        if handler not in self._handlers[key]:
            self._handlers[key].append(handler)

    def unsubscribe(
        self,
        event_name: str,
        handler: EventHandler,
    ) -> None:
        key = str(event_name).strip()

        if key == "*":
            if handler in self._wildcard_handlers:
                self._wildcard_handlers.remove(handler)
            return

        handlers = self._handlers.get(key, [])

        if handler in handlers:
            handlers.remove(handler)

    def publish(
        self,
        event_name: str,
        payload: Any = None,
        source: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Event:
        event = Event(
            name=str(event_name).strip(),
            payload=payload,
            source=str(source),
            metadata=dict(metadata or {}),
        )

        self.history.append(event)

        handlers = list(
            self._handlers.get(event.name, [])
        )

        handlers.extend(
            self._wildcard_handlers
        )

        for handler in handlers:
            handler(event)

        return event

    def clear(self) -> None:
        self._handlers.clear()
        self._wildcard_handlers.clear()
        self.history.clear()

    def subscriber_count(
        self,
        event_name: str,
    ) -> int:
        key = str(event_name).strip()

        if key == "*":
            return len(self._wildcard_handlers)

        return len(
            self._handlers.get(key, [])
        )
