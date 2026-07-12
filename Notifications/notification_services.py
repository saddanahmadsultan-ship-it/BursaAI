"""
=========================================================
BursaAI Notification Service Registration
Version : 6.0 Sprint 6C
=========================================================
"""

from __future__ import annotations

from typing import Iterable, Optional

from Framework.service_container import ServiceContainer
from Notifications.base_notifier import BaseNotifier
from Notifications.notification_hub import NotificationHub
from Notifications.telegram_notifier import TelegramNotifier


def register_notification_hub(
    services: ServiceContainer,
    *,
    notifiers: Optional[
        Iterable[BaseNotifier]
    ] = None,
    telegram_enabled: bool = False,
    telegram_dry_run: bool = False,
) -> NotificationHub:
    event_bus = services.resolve(
        "event_bus"
    )

    configured = list(
        notifiers or []
    )

    if telegram_enabled:
        configured.append(
            TelegramNotifier(
                enabled=True,
                dry_run=telegram_dry_run,
            )
        )

    hub = NotificationHub(
        event_bus=event_bus,
        notifiers=configured,
    )

    hub.attach()

    services.register_instance(
        "notification_hub",
        hub,
        replace=True,
    )

    return hub
