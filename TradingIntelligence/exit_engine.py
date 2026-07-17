from __future__ import annotations

from dataclasses import dataclass

from TradingIntelligence.position_config import PositionIntelligenceConfig
from TradingIntelligence.position_contracts import PositionCandidate


@dataclass
class ExitLevels:
    stop_loss: float
    target_price: float
    risk_reward: float


class ExitLevelEngine:
    def __init__(
        self,
        config: PositionIntelligenceConfig | None = None,
    ) -> None:
        self.config = config or PositionIntelligenceConfig()

    def calculate(
        self,
        candidate: PositionCandidate,
        entry_price: float,
    ) -> ExitLevels:
        atr = max(float(candidate.atr), entry_price * 0.005)

        stop_distance = atr * self.config.atr_stop_multiplier
        target_distance = atr * self.config.atr_target_multiplier

        stop_loss = entry_price - stop_distance

        if (
            candidate.support_price
            and candidate.support_price > 0
            and candidate.support_price < entry_price
        ):
            technical_stop = candidate.support_price - atr * 0.25
            stop_loss = min(stop_loss, technical_stop)

        target_price = entry_price + target_distance

        if (
            candidate.resistance_price
            and candidate.resistance_price > entry_price
        ):
            resistance_target = candidate.resistance_price
            if resistance_target > entry_price + stop_distance:
                target_price = max(
                    target_price,
                    resistance_target,
                )

        stop_loss = max(stop_loss, entry_price * 0.50)
        risk = entry_price - stop_loss
        reward = target_price - entry_price
        rr = reward / risk if risk > 0 else 0.0

        return ExitLevels(
            stop_loss=round(stop_loss, 4),
            target_price=round(target_price, 4),
            risk_reward=round(rr, 4),
        )
