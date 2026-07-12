"""
=========================================================
BursaAI Performance Report
Version : 6.0 Sprint 6E
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from Analytics.performance_models import (
    PerformanceMetrics,
)


@dataclass(slots=True)
class PerformanceReport:
    metrics: PerformanceMetrics

    def render_text(self) -> str:
        value = self.metrics

        profit_factor = (
            "INF"
            if value.profit_factor == float("inf")
            else f"{value.profit_factor:.2f}"
        )

        return "\n".join(
            [
                "=" * 54,
                "BURSAAI PERFORMANCE REPORT",
                "=" * 54,
                f"Total Trades          : {value.total_trades}",
                f"Winning Trades        : {value.winning_trades}",
                f"Losing Trades         : {value.losing_trades}",
                f"Win Rate              : {value.win_rate:.2f}%",
                f"Profit Factor         : {profit_factor}",
                f"Expectancy            : RM{value.expectancy:,.2f}",
                f"Average Winner        : RM{value.average_winner:,.2f}",
                f"Average Loser         : RM{value.average_loser:,.2f}",
                f"Maximum Drawdown      : {value.maximum_drawdown_percent:.2f}%",
                f"Sharpe Ratio          : {value.sharpe_ratio:.2f}",
                f"Sortino Ratio         : {value.sortino_ratio:.2f}",
                f"Recovery Factor       : {value.recovery_factor:.2f}",
                f"Kelly                 : {value.kelly_percent:.2f}%",
                f"Portfolio Return      : {value.portfolio_return_percent:.2f}%",
                f"Ending Capital        : RM{value.ending_capital:,.2f}",
                "=" * 54,
            ]
        )
