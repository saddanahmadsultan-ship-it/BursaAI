"""
=========================================================
BursaAI Journal Service Registration
Version : 6.0 Sprint 6D
=========================================================
"""

from __future__ import annotations

from Framework.service_container import (
    ServiceContainer,
)
from Journal.event_journal_bridge import (
    EventJournalBridge,
)
from Journal.trade_journal import (
    TradeJournal,
)


def register_trade_journal(
    services: ServiceContainer,
    *,
    database_path: str = "Data/bursaai_journal.db",
    attach_events: bool = True,
) -> TradeJournal:
    journal = TradeJournal(
        database_path=database_path
    )

    services.register_instance(
        "trade_journal",
        journal,
        replace=True,
    )

    if attach_events:
        event_bus = services.resolve(
            "event_bus"
        )

        bridge = EventJournalBridge(
            event_bus=event_bus,
            journal=journal,
        )

        bridge.attach()

        services.register_instance(
            "event_journal_bridge",
            bridge,
            replace=True,
        )

    return journal
