"""
=========================================================
BursaAI Paper Position
Version : 6.0 Sprint 6B
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PaperPosition:
    symbol: str
    shares: int = 0
    average_price: float = 0.0
    market_price: float = 0.0
    realized_pnl: float = 0.0

    @property
    def market_value(self) -> float:
        return round(
            self.shares * self.market_price,
            2,
        )

    @property
    def cost_basis(self) -> float:
        return round(
            self.shares * self.average_price,
            2,
        )

    @property
    def unrealized_pnl(self) -> float:
        return round(
            self.market_value - self.cost_basis,
            2,
        )

    def buy(self, shares: int, price: float) -> None:
        shares = max(int(shares), 0)
        price = max(float(price), 0.0)

        if shares <= 0:
            return

        old_cost = self.shares * self.average_price
        new_cost = shares * price
        new_total = self.shares + shares

        self.shares = new_total
        self.average_price = (
            (old_cost + new_cost) / new_total
            if new_total > 0
            else 0.0
        )
        self.market_price = price

    def sell(self, shares: int, price: float) -> float:
        shares = min(
            max(int(shares), 0),
            self.shares,
        )
        price = max(float(price), 0.0)

        if shares <= 0:
            return 0.0

        pnl = (
            price - self.average_price
        ) * shares

        self.realized_pnl += pnl
        self.shares -= shares
        self.market_price = price

        if self.shares == 0:
            self.average_price = 0.0

        return round(pnl, 2)

    def update_market_price(self, price: float) -> None:
        self.market_price = max(float(price), 0.0)
