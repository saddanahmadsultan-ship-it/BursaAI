"""
BursaAI v6.0 Sprint 6C Notification Hub test.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Framework.infrastructure import (
    build_infrastructure,
)
from Notifications.base_notifier import BaseNotifier
from Notifications.notification_message import (
    NotificationMessage,
)
from Notifications.notification_services import (
    register_notification_hub,
)
from Notifications.telegram_notifier import (
    TelegramNotifier,
)


class MemoryNotifier(BaseNotifier):
    name = "Memory Notifier"

    def __init__(self):
        super().__init__(enabled=True)
        self.messages = []

    def send(self, message):
        self.messages.append(message)

        return {
            "success": True,
            "notifier": self.name,
            "text": message.render_text(),
        }


def main():
    infrastructure = build_infrastructure()
    memory = MemoryNotifier()

    hub = register_notification_hub(
        infrastructure.services,
        notifiers=[memory],
    )

    infrastructure.events.publish(
        "PortfolioAllocated",
        payload={
            "capital_allocated": 50000,
            "remaining_cash": 50000,
            "portfolio_risk_pct": 2.5,
            "active_positions": 3,
            "status": "ALLOCATED",
        },
        source="Test",
    )

    assert len(memory.messages) == 1
    assert (
        memory.messages[0].event_name
        == "PortfolioAllocated"
    )
    assert "Portfolio Allocated" in (
        memory.messages[0].title
    )
    assert len(hub.history) == 1
    assert hub.history[0]["success"] is True

    telegram = TelegramNotifier(
        bot_token="TEST_TOKEN",
        chat_id="123456",
        dry_run=True,
    )

    response = telegram.send(
        NotificationMessage(
            title="Test",
            body="Hello",
        )
    )

    assert response["success"] is True
    assert response["dry_run"] is True
    assert (
        response["payload"]["chat_id"]
        == "123456"
    )
    assert (
        response["payload"]["text"]
        == "Test\n\nHello"
    )

    unconfigured = TelegramNotifier(
        bot_token="",
        chat_id="",
    )

    skipped = unconfigured.send(
        NotificationMessage(
            title="Test",
            body="Hello",
        )
    )

    assert skipped["success"] is False
    assert skipped["skipped"] is True

    hub.detach()

    infrastructure.events.publish(
        "ExecutionCompleted",
        payload={},
    )

    assert len(memory.messages) == 1

    print("=" * 88)
    print("BURSAAI v6.0 SPRINT 6C TEST")
    print("=" * 88)
    print("Notification Message      : OK")
    print("Base Notifier             : OK")
    print("Notification Hub          : OK")
    print("Event Subscription        : OK")
    print("Message Formatter         : OK")
    print("Notification History      : OK")
    print("Telegram Dry Run          : OK")
    print("Missing Config Handling   : OK")
    print("Hub Detach                : OK")
    print("=" * 88)
    print("SPRINT 6C NOTIFICATION HUB OK")


if __name__ == "__main__":
    main()
