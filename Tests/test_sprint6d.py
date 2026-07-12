"""
BursaAI v6.0 Sprint 6D Trade Journal test.
"""

from pathlib import Path
import sys
import tempfile

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Framework.infrastructure import (
    build_infrastructure,
)
from Journal.journal_models import (
    JournalEvent,
    JournalRecord,
)
from Journal.journal_services import (
    register_trade_journal,
)


def main():
    infrastructure = build_infrastructure()

    with tempfile.TemporaryDirectory() as folder:
        database = Path(folder) / "journal.db"

        journal = register_trade_journal(
            infrastructure.services,
            database_path=str(database),
            attach_events=True,
        )

        journal.add(
            JournalRecord(
                event_type=JournalEvent.TRADE,
                symbol="1155.KL",
                action="SELL",
                quantity=1000,
                price=10.60,
                pnl=580.0,
                score=88,
                confidence=92,
                signal="BUY",
                status="CLOSED",
                notes="Target reached",
            )
        )

        infrastructure.events.publish(
            "DecisionCompleted",
            payload={
                "symbol": "1023.KL",
                "recommendation": "WATCH",
                "rating": "B+",
                "quality": 68,
                "summary": "Watchlist candidate",
            },
            source="Test",
        )

        infrastructure.events.publish(
            "PaperOrderUpdated",
            payload={
                "symbol": "1295.KL",
                "side": "BUY",
                "status": "FILLED",
                "filled_shares": 2000,
                "filled_price": 4.90,
                "cash": 90000,
            },
            source="Test",
        )

        assert journal.count() == 3

        records = journal.list_records(
            limit=10
        )

        assert len(records) == 3

        stock_records = journal.list_records(
            symbol="1155.KL"
        )

        assert len(stock_records) == 1
        assert stock_records[0]["pnl"] == 580.0

        decision_records = journal.list_records(
            event_type=JournalEvent.DECISION
        )

        assert len(decision_records) == 1
        assert (
            decision_records[0]["signal"]
            == "WATCH"
        )

        summary = journal.summary()

        assert summary["records"] == 3
        assert summary["realized_pnl"] == 580.0
        assert summary["winning_records"] == 1
        assert summary["losing_records"] == 0

        assert database.exists()

    print("=" * 88)
    print("BURSAAI v6.0 SPRINT 6D TEST")
    print("=" * 88)
    print("Journal Models           : OK")
    print("SQLite Journal           : OK")
    print("Database Initialization  : OK")
    print("Manual Record            : OK")
    print("Event Journal Bridge     : OK")
    print("Decision Recording       : OK")
    print("Order Recording          : OK")
    print("Journal Query            : OK")
    print("Journal Summary          : OK")
    print("Persistent Database      : OK")
    print("=" * 88)
    print("SPRINT 6D TRADE JOURNAL OK")


if __name__ == "__main__":
    main()
