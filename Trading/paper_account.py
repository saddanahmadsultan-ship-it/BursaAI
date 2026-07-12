"""
=========================================================
BursaAI Paper Account
Version : 6.0 Sprint 6B
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from Trading.paper_position import PaperPosition


@dataclass
class PaperAccount:
    starting_capital: float = 100000.0
    cash: float = 100000.0
    positions: Dict[str, PaperPosition] = field(
        default_factory=dict
    )
    total_commission: float = 0.0
    realized_pnl: float = 0.0

    def __post_init__(self) -> None:
        self.starting_capital = max(
            float(self.starting_capital),
            0.0,
        )

        if self.cash == 100000.0 and self.starting_capital != 100000.0:
            self.cash = self.starting_capital

        self.cash = max(float(self.cash), 0.0)

    def get_position(self, symbol: str) -> PaperPosition:
        if symbol not in self.positions:
            self.positions[symbol] = PaperPosition(
                symbol=symbol
            )

        return self.positions[symbol]

    @property
    def market_value(self) -> float:
        return round(
            sum(
                position.market_value
                for position in self.positions.values()
            ),
            2,
        )

    @property
    def unrealized_pnl(self) -> float:
        return round(
            sum(
                position.unrealized_pnl
                for position in self.positions.values()
            ),
            2,
        )

    @property
    def equity(self) -> float:
        return round(
            self.cash + self.market_value,
            2,
        )

    @property
    def total_return(self) -> float:
        if self.starting_capital <= 0:
            return 0.0

        return round(
            (
                self.equity
                - self.starting_capital
            )
            / self.starting_capital
            * 100,
            4,
        )
