from __future__ import annotations

from TradingIntelligence.position_config import PositionIntelligenceConfig
from TradingIntelligence.position_contracts import (
    PositionCandidate,
    PositionRiskProfile,
)


class PositionPlanValidator:
    def __init__(
        self,
        config: PositionIntelligenceConfig | None = None,
    ) -> None:
        self.config = config or PositionIntelligenceConfig()

    def validate_candidate(
        self,
        candidate: PositionCandidate,
        profile: PositionRiskProfile,
    ) -> tuple[bool, list[str]]:
        reasons: list[str] = []

        if candidate.price <= 0:
            reasons.append("Invalid market price")

        if candidate.atr <= 0:
            reasons.append("ATR must be positive")

        if candidate.final_score < self.config.minimum_final_score:
            reasons.append("Final score below minimum threshold")

        if candidate.confidence < self.config.minimum_confidence:
            reasons.append("Confidence below minimum threshold")

        if candidate.ml_probability < self.config.minimum_ml_probability:
            reasons.append("ML probability below minimum threshold")

        if self.config.signal_risk_multiplier.get(
            candidate.signal.upper(),
            0.0,
        ) <= 0:
            reasons.append("Signal is not eligible for a new position")

        if profile.active_positions >= self.config.maximum_active_positions:
            reasons.append("Maximum active positions reached")

        if (
            profile.sector_exposure_percent
            >= self.config.maximum_sector_exposure_percent
        ):
            reasons.append("Maximum sector exposure reached")

        if profile.available_capital <= 0:
            reasons.append("No available capital")

        return len(reasons) == 0, reasons
