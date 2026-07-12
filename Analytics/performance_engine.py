"""
=========================================================
BursaAI Performance Engine
Version : 6.0 Sprint 6E
=========================================================
"""

from __future__ import annotations

from typing import Dict, List

from Analytics.metrics import (
    build_equity_curve,
    calculate_monthly_returns,
    maximum_drawdown,
    maximum_streaks,
)
from Analytics.performance_models import (
    PerformanceMetrics,
)
from Analytics.statistics import (
    sharpe_ratio,
    sortino_ratio,
)
from Journal.journal_models import JournalEvent
from Journal.trade_journal import TradeJournal


class PerformanceEngine:
    def __init__(
        self,
        journal: TradeJournal,
        starting_capital: float = 100000.0,
    ):
        self.journal = journal
        self.starting_capital = max(
            float(starting_capital),
            0.0,
        )

    def _trade_records(self) -> List[Dict]:
        records = self.journal.list_records(
            limit=100000
        )

        return [
            record
            for record in reversed(records)
            if record.get("event_type")
            in {
                JournalEvent.TRADE.value,
                JournalEvent.ORDER.value,
            }
            and float(
                record.get("pnl", 0) or 0
            ) != 0
        ]

    def calculate(self) -> PerformanceMetrics:
        records = self._trade_records()
        pnls = [
            float(record.get("pnl", 0) or 0)
            for record in records
        ]

        winners = [
            value for value in pnls
            if value > 0
        ]
        losers = [
            value for value in pnls
            if value < 0
        ]
        breakeven = [
            value for value in pnls
            if value == 0
        ]

        total = len(pnls)
        winning = len(winners)
        losing = len(losers)

        gross_profit = sum(winners)
        gross_loss = abs(sum(losers))
        net_profit = sum(pnls)

        average_winner = (
            gross_profit / winning
            if winning
            else 0.0
        )

        average_loser = (
            gross_loss / losing
            if losing
            else 0.0
        )

        profit_factor = (
            gross_profit / gross_loss
            if gross_loss > 0
            else (
                float("inf")
                if gross_profit > 0
                else 0.0
            )
        )

        payoff_ratio = (
            average_winner / average_loser
            if average_loser > 0
            else 0.0
        )

        expectancy = (
            net_profit / total
            if total
            else 0.0
        )

        win_rate = (
            winning / total * 100
            if total
            else 0.0
        )

        loss_rate = (
            losing / total * 100
            if total
            else 0.0
        )

        curve = build_equity_curve(
            pnls,
            self.starting_capital,
        )

        max_dd_amount, max_dd_percent = (
            maximum_drawdown(curve)
        )

        returns = []

        for previous, current in zip(
            curve,
            curve[1:],
        ):
            if previous > 0:
                returns.append(
                    (
                        current - previous
                    )
                    / previous
                )

        sharpe = sharpe_ratio(returns)
        sortino = sortino_ratio(returns)

        ending_capital = (
            curve[-1]
            if curve
            else self.starting_capital
        )

        portfolio_return = (
            (
                ending_capital
                - self.starting_capital
            )
            / self.starting_capital
            * 100
            if self.starting_capital > 0
            else 0.0
        )

        calmar = (
            portfolio_return
            / max_dd_percent
            if max_dd_percent > 0
            else 0.0
        )

        recovery = (
            net_profit
            / max_dd_amount
            if max_dd_amount > 0
            else 0.0
        )

        win_probability = (
            winning / total
            if total
            else 0.0
        )

        loss_probability = (
            losing / total
            if total
            else 0.0
        )

        kelly = (
            (
                win_probability
                - (
                    loss_probability
                    / payoff_ratio
                )
            )
            * 100
            if payoff_ratio > 0
            else 0.0
        )

        max_wins, max_losses = (
            maximum_streaks(pnls)
        )

        return PerformanceMetrics(
            total_trades=total,
            winning_trades=winning,
            losing_trades=losing,
            breakeven_trades=len(breakeven),
            win_rate=round(win_rate, 4),
            loss_rate=round(loss_rate, 4),
            gross_profit=round(gross_profit, 2),
            gross_loss=round(gross_loss, 2),
            net_profit=round(net_profit, 2),
            profit_factor=round(profit_factor, 4)
            if profit_factor != float("inf")
            else float("inf"),
            expectancy=round(expectancy, 2),
            average_trade=round(expectancy, 2),
            average_winner=round(
                average_winner,
                2,
            ),
            average_loser=round(
                average_loser,
                2,
            ),
            payoff_ratio=round(
                payoff_ratio,
                4,
            ),
            maximum_drawdown_amount=(
                max_dd_amount
            ),
            maximum_drawdown_percent=(
                max_dd_percent
            ),
            sharpe_ratio=round(sharpe, 4),
            sortino_ratio=round(sortino, 4),
            calmar_ratio=round(calmar, 4),
            recovery_factor=round(
                recovery,
                4,
            ),
            kelly_percent=round(
                max(kelly, 0.0),
                4,
            ),
            maximum_consecutive_wins=max_wins,
            maximum_consecutive_losses=(
                max_losses
            ),
            starting_capital=round(
                self.starting_capital,
                2,
            ),
            ending_capital=round(
                ending_capital,
                2,
            ),
            portfolio_return_percent=round(
                portfolio_return,
                4,
            ),
            equity_curve=curve,
            monthly_returns=(
                calculate_monthly_returns(
                    records
                )
            ),
        )
