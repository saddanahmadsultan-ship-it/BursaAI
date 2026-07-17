from __future__ import annotations

from TradingIntelligence.position_config import PositionIntelligenceConfig
from TradingIntelligence.position_contracts import (
    PositionCandidate,
    PositionRiskProfile,
)


class RiskBudgetAllocator:
    def __init__(
        self,
        config: PositionIntelligenceConfig | None = None,
    ) -> None:
        self.config = config or PositionIntelligenceConfig()

    def allocate(
        self,
        candidate: PositionCandidate,
        profile: PositionRiskProfile,
        quality_score: float,
    ) -> tuple[float, float, list[str]]:
        reasons: list[str] = []

        signal_multiplier = self.config.signal_risk_multiplier.get(
            candidate.signal.upper(),
            0.0,
        )

        quality_multiplier = max(0.25, min(quality_score / 80.0, 1.25))
        confidence_multiplier = max(
            0.50,
            min(candidate.confidence / 80.0, 1.20),
        )
        ml_multiplier = max(
            0.50,
            min(candidate.ml_probability / 0.70, 1.20),
        )

        risk_percent = (
            self.config.base_risk_percent
            * signal_multiplier
            * quality_multiplier
            * confidence_multiplier
            * ml_multiplier
        )

        if candidate.volatility_percent > self.config.volatility_penalty_threshold:
            risk_percent *= 0.70
            reasons.append("Risk reduced due to elevated volatility")

        if profile.current_drawdown_percent >= self.config.drawdown_guard_percent:
            risk_percent *= 0.50
            reasons.append("Risk reduced by portfolio drawdown guard")

        remaining_portfolio_risk = max(
            0.0,
            5.0 - profile.current_portfolio_risk_percent,
        )

        risk_percent = min(
            risk_percent,
            self.config.maximum_risk_percent,
            remaining_portfolio_risk,
        )

        if risk_percent > 0:
            risk_percent = max(
                risk_percent,
                self.config.minimum_risk_percent,
            )

        capital_at_risk = (
            profile.portfolio_capital
            * risk_percent
            / 100.0
        )

        return (
            round(risk_percent, 4),
            round(capital_at_risk, 2),
            reasons,
        )
