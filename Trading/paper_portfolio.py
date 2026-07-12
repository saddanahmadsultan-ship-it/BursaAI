"""
=========================================================
BursaAI Paper Portfolio
Version : 6.0 Sprint 6B
=========================================================
"""

from __future__ import annotations

from typing import Any, Dict, Iterable

from Framework.context import AnalysisContext
from Trading.paper_account import PaperAccount
from Trading.paper_execution import PaperExecutionEngine
from Trading.paper_order import (
    OrderSide,
    PaperOrder,
)


class PaperPortfolio:
    """
    Converts allocated BursaAI contexts into paper BUY orders.
    """

    def __init__(
        self,
        account: PaperAccount,
        execution_engine: PaperExecutionEngine,
    ):
        self.account = account
        self.execution_engine = execution_engine

    def open_allocated_positions(
        self,
        contexts: Iterable[AnalysisContext],
    ) -> Dict[str, Any]:
        orders = []

        for context in contexts:
            portfolio = context.analysis.portfolio
            trade = context.analysis.trade

            if portfolio.status not in {
                "ALLOCATED",
                "REDUCED",
            }:
                continue

            shares = portfolio.allocated_shares
            price = trade.entry or context.analysis.identity.price

            if shares <= 0 or price <= 0:
                continue

            order = PaperOrder(
                symbol=context.symbol,
                side=OrderSide.BUY,
                shares=shares,
                price=price,
            )

            orders.append(
                self.execution_engine.execute(order)
            )

        return {
            "orders": orders,
            "cash": round(
                self.account.cash,
                2,
            ),
            "market_value": self.account.market_value,
            "equity": self.account.equity,
            "realized_pnl": round(
                self.account.realized_pnl,
                2,
            ),
            "unrealized_pnl": self.account.unrealized_pnl,
            "total_return_pct": self.account.total_return,
        }

    def update_prices(
        self,
        prices: Dict[str, float],
    ) -> None:
        for symbol, price in prices.items():
            position = self.account.positions.get(
                symbol
            )

            if position is not None:
                position.update_market_price(
                    price
                )

    def close_position(
        self,
        symbol: str,
        price: float,
    ) -> PaperOrder | None:
        position = self.account.positions.get(
            symbol
        )

        if position is None or position.shares <= 0:
            return None

        order = PaperOrder(
            symbol=symbol,
            side=OrderSide.SELL,
            shares=position.shares,
            price=price,
        )

        return self.execution_engine.execute(
            order
        )
