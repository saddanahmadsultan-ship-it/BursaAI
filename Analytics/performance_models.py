"""
=========================================================
BursaAI Performance Models
Version : 6.0 Sprint 6E
=========================================================
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List


@dataclass(slots=True)
class PerformanceMetrics:
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    breakeven_trades: int = 0

    win_rate: float = 0.0
    loss_rate: float = 0.0

    gross_profit: float = 0.0
    gross_loss: float = 0.0
    net_profit: float = 0.0

    profit_factor: float = 0.0
    expectancy: float = 0.0
    average_trade: float = 0.0
    average_winner: float = 0.0
    average_loser: float = 0.0
    payoff_ratio: float = 0.0

    maximum_drawdown_amount: float = 0.0
    maximum_drawdown_percent: float = 0.0

    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    recovery_factor: float = 0.0
    kelly_percent: float = 0.0

    maximum_consecutive_wins: int = 0
    maximum_consecutive_losses: int = 0

    starting_capital: float = 0.0
    ending_capital: float = 0.0
    portfolio_return_percent: float = 0.0

    equity_curve: List[float] = field(default_factory=list)
    monthly_returns: Dict[str, float] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)
