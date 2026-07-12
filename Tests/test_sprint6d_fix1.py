"""
BursaAI v6.0 Sprint 6D Fix 1 test.
"""

from pathlib import Path
import sys
import tempfile

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Framework.infrastructure import build_infrastructure
from Journal.journal_models import JournalEvent, JournalRecord
from Journal.journal_services import register_trade_journal


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
        assert len(journal.list_records(limit=10)) == 3

        summary = journal.summary()

        assert summary["records"] == 3
        assert summary["realized_pnl"] == 580.0

        journal.close()

        assert database.exists()

    print("=" * 88)
    print("BURSAAI v6.0 SPRINT 6D FIX 1 TEST")
    print("=" * 88)
    print("Explicit SQLite Close    : OK")
    print("Windows Temp Cleanup     : OK")
    print("Journal Write / Read     : OK")
    print("Event Journal Bridge     : OK")
    print("=" * 88)
    print("SPRINT 6D WINDOWS SQLITE FIX OK")


if __name__ == "__main__":
    main()
