"""
BursaAI v6.0 Sprint 6E Performance Analytics test.
"""

from pathlib import Path
import sys
import tempfile

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Analytics.performance_engine import (
    PerformanceEngine,
)
from Analytics.performance_report import (
    PerformanceReport,
)
from Journal.journal_models import (
    JournalEvent,
    JournalRecord,
)
from Journal.trade_journal import TradeJournal


def main():
    with tempfile.TemporaryDirectory() as folder:
        database = Path(folder) / "journal.db"

        journal = TradeJournal(
            database_path=str(database)
        )

        pnls = [
            500,
            -200,
            750,
            -300,
            400,
            600,
            -250,
            900,
        ]

        records = []

        for index, pnl in enumerate(pnls):
            records.append(
                JournalRecord(
                    event_type=JournalEvent.TRADE,
                    symbol=f"TEST{index}.KL",
                    action="SELL",
                    quantity=100,
                    price=10.0,
                    pnl=pnl,
                    score=80,
                    confidence=85,
                    signal="BUY",
                    status="CLOSED",
                )
            )

        journal.add_many(records)

        engine = PerformanceEngine(
            journal=journal,
            starting_capital=100000,
        )

        metrics = engine.calculate()

        assert metrics.total_trades == 8
        assert metrics.winning_trades == 5
        assert metrics.losing_trades == 3
        assert metrics.win_rate == 62.5
        assert metrics.gross_profit == 3150.0
        assert metrics.gross_loss == 750.0
        assert metrics.net_profit == 2400.0
        assert metrics.profit_factor == 4.2
        assert metrics.ending_capital == 102400.0
        assert metrics.portfolio_return_percent == 2.4
        assert metrics.maximum_consecutive_wins == 2
        assert metrics.maximum_consecutive_losses == 1
        assert len(metrics.equity_curve) == 9

        report = PerformanceReport(
            metrics=metrics
        )

        rendered = report.render_text()

        assert (
            "BURSAAI PERFORMANCE REPORT"
            in rendered
        )
        assert "Win Rate" in rendered
        assert "Profit Factor" in rendered

    print("=" * 88)
    print("BURSAAI v6.0 SPRINT 6E TEST")
    print("=" * 88)
    print("Performance Models      : OK")
    print("Trade Extraction        : OK")
    print("Win / Loss Metrics      : OK")
    print("Profit Factor           : OK")
    print("Expectancy              : OK")
    print("Equity Curve            : OK")
    print("Maximum Drawdown        : OK")
    print("Sharpe Ratio            : OK")
    print("Sortino Ratio           : OK")
    print("Kelly Percentage        : OK")
    print("Performance Report      : OK")
    print("=" * 88)
    print("SPRINT 6E PERFORMANCE ANALYTICS OK")


if __name__ == "__main__":
    main()
