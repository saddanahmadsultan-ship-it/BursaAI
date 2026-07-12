"""
=========================================================
BursaAI Notification Hub
Version : 6.0 Sprint 6C
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List

from Framework.event_bus import Event, EventBus
from Notifications.base_notifier import BaseNotifier
from Notifications.message_formatter import (
    format_event_message,
)
from Notifications.notification_message import (
    NotificationMessage,
)


@dataclass(slots=True)
class NotificationResult:
    notifier: str
    success: bool
    data: Dict[str, Any]


class NotificationHub:
    """
    Routes BursaAI events to one or more notifiers.
    """

    DEFAULT_EVENTS = {
        "ExecutionStarted",
        "ExecutionCompleted",
        "ExecutionFailed",
        "PortfolioAllocated",
        "PaperOrderUpdated",
        "DecisionCompleted",
    }

    def __init__(
        self,
        event_bus: EventBus,
        notifiers: Iterable[BaseNotifier] | None = None,
        subscribed_events: Iterable[str] | None = None,
    ):
        self.event_bus = event_bus
        self.notifiers: List[BaseNotifier] = list(
            notifiers or []
        )
        self.subscribed_events = set(
            subscribed_events
            or self.DEFAULT_EVENTS
        )
        self.history: List[Dict[str, Any]] = []
        self._attached = False

    def add_notifier(
        self,
        notifier: BaseNotifier,
    ) -> None:
        self.notifiers.append(notifier)

    def attach(self) -> None:
        if self._attached:
            return

        for event_name in self.subscribed_events:
            self.event_bus.subscribe(
                event_name,
                self._handle_event,
            )

        self._attached = True

    def detach(self) -> None:
        if not self._attached:
            return

        for event_name in self.subscribed_events:
            self.event_bus.unsubscribe(
                event_name,
                self._handle_event,
            )

        self._attached = False

    def _handle_event(
        self,
        event: Event,
    ) -> None:
        message = format_event_message(
            event.name,
            event.payload
            if isinstance(event.payload, dict)
            else {"payload": event.payload},
        )

        self.broadcast(message)

    def broadcast(
        self,
        message: NotificationMessage,
    ) -> List[NotificationResult]:
        results: List[NotificationResult] = []

        for notifier in self.notifiers:
            data = notifier.send(message)

            result = NotificationResult(
                notifier=notifier.name,
                success=bool(
                    data.get("success", False)
                ),
                data=data,
            )

            results.append(result)

            self.history.append(
                {
                    "message_id": message.message_id,
                    "event_name": message.event_name,
                    "notifier": notifier.name,
                    "success": result.success,
                    "data": data,
                }
            )

        return results
