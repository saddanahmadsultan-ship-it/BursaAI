"""
=========================================================
BursaAI Base Notifier
Version : 6.0 Sprint 6C
=========================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from Notifications.notification_message import (
    NotificationMessage,
)


class BaseNotifier(ABC):
    name = "Base Notifier"

    def __init__(self, enabled: bool = True):
        self.enabled = bool(enabled)

    @abstractmethod
    def send(
        self,
        message: NotificationMessage,
    ) -> Dict[str, Any]:
        ...

    def enable(self) -> None:
        self.enabled = True

    def disable(self) -> None:
        self.enabled = False
