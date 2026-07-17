from __future__ import annotations

import math

from TradingIntelligence.position_config import PositionIntelligenceConfig


class PositionSizingEngine:
    def __init__(
        self,
        config: PositionIntelligenceConfig | None = None,
    ) -> None:
        self.config = config or PositionIntelligenceConfig()

    def calculate(
        self,
        entry_price: float,
        stop_loss: float,
        capital_at_risk: float,
        available_capital: float,
    ) -> tuple[int, int, float]:
        risk_per_share = max(entry_price - stop_loss, 0.0)

        if (
            risk_per_share <= 0
            or capital_at_risk <= 0
            or entry_price <= 0
        ):
            return 0, 0, 0.0

        risk_quantity = math.floor(
            capital_at_risk / risk_per_share
        )

        max_position_value = min(
            available_capital,
            self.config.portfolio_capital
            * self.config.maximum_position_percent
            / 100.0,
        )

        capital_quantity = math.floor(
            max_position_value / entry_price
        )

        quantity = max(
            0,
            min(risk_quantity, capital_quantity),
        )

        if self.config.round_lot:
            quantity = (
                quantity // self.config.lot_size
            ) * self.config.lot_size

        lot_count = (
            quantity // self.config.lot_size
            if self.config.lot_size > 0
            else 0
        )

        position_value = quantity * entry_price

        return (
            int(quantity),
            int(lot_count),
            round(position_value, 2),
        )
