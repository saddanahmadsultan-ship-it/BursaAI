"""
=========================================================
BursaAI Paper Execution Engine
Version : 6.0 Sprint 6B
=========================================================
"""

from __future__ import annotations

from typing import Callable, Optional

from Framework.event_bus import EventBus
from Framework.service_container import ServiceContainer
from Trading.paper_account import PaperAccount
from Trading.paper_order import (
    OrderSide,
    PaperOrder,
)


class PaperExecutionEngine:
    """
    Executes market orders against a simulated account.
    """

    def __init__(
        self,
        account: PaperAccount,
        commission_function: Optional[
            Callable[[PaperOrder], float]
        ] = None,
        slippage_percent: float = 0.0,
        services: Optional[ServiceContainer] = None,
        event_bus: Optional[EventBus] = None,
    ):
        self.account = account
        self.commission_function = (
            commission_function
            or (lambda order: 0.0)
        )
        self.slippage_percent = max(
            float(slippage_percent),
            0.0,
        )
        self.orders: list[PaperOrder] = []

        if event_bus is not None:
            self.event_bus = event_bus
        elif services is not None and services.contains("event_bus"):
            self.event_bus = services.resolve(
                "event_bus"
            )
        else:
            self.event_bus = None

    def _fill_price(self, order: PaperOrder) -> float:
        adjustment = (
            self.slippage_percent / 100.0
        )

        if order.side == OrderSide.BUY:
            return order.price * (1 + adjustment)

        return order.price * (1 - adjustment)

    def execute(self, order: PaperOrder) -> PaperOrder:
        if order.shares <= 0:
            order.reject("INVALID SHARE QUANTITY")
            self.orders.append(order)
            self._publish(order)
            return order

        fill_price = round(
            self._fill_price(order),
            4,
        )

        commission = max(
            float(
                self.commission_function(order)
            ),
            0.0,
        )

        position = self.account.get_position(
            order.symbol
        )

        if order.side == OrderSide.BUY:
            required_cash = (
                fill_price * order.shares
                + commission
            )

            if required_cash > self.account.cash:
                order.reject("INSUFFICIENT CASH")
                self.orders.append(order)
                self._publish(order)
                return order

            self.account.cash -= required_cash
            self.account.total_commission += commission
            position.buy(
                shares=order.shares,
                price=fill_price,
            )

        elif order.side == OrderSide.SELL:
            if order.shares > position.shares:
                order.reject("INSUFFICIENT SHARES")
                self.orders.append(order)
                self._publish(order)
                return order

            proceeds = (
                fill_price * order.shares
                - commission
            )

            realized = position.sell(
                shares=order.shares,
                price=fill_price,
            )

            self.account.cash += proceeds
            self.account.total_commission += commission
            self.account.realized_pnl += (
                realized - commission
            )

        order.fill(
            filled_price=fill_price,
            filled_shares=order.shares,
            commission=commission,
        )

        self.orders.append(order)
        self._publish(order)

        return order

    def _publish(self, order: PaperOrder) -> None:
        if self.event_bus is None:
            return

        self.event_bus.publish(
            "PaperOrderUpdated",
            payload={
                "order_id": order.order_id,
                "symbol": order.symbol,
                "side": order.side.value,
                "status": order.status.value,
                "shares": order.shares,
                "filled_shares": order.filled_shares,
                "price": order.price,
                "filled_price": order.filled_price,
                "commission": order.commission,
                "reason": order.reason,
                "cash": round(
                    self.account.cash,
                    2,
                ),
                "equity": self.account.equity,
            },
            source="Paper Execution Engine",
        )
