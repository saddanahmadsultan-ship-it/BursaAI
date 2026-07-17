from __future__ import annotations

from TradingIntelligence.position_config import PositionIntelligenceConfig
from TradingIntelligence.position_contracts import PositionCandidate


class PositionQualityScorer:
    def __init__(
        self,
        config: PositionIntelligenceConfig | None = None,
    ) -> None:
        self.config = config or PositionIntelligenceConfig()

    def score(self, candidate: PositionCandidate) -> float:
        signal_multiplier = self.config.signal_risk_multiplier.get(
            candidate.signal.upper(),
            0.0,
        )

        score_component = min(max(candidate.final_score, 0.0), 100.0) * 0.30
        confidence_component = min(max(candidate.confidence, 0.0), 100.0) * 0.25
        ml_component = min(max(candidate.ml_probability, 0.0), 1.0) * 100.0 * 0.25
        signal_component = min(signal_multiplier, 1.20) / 1.20 * 100.0 * 0.20

        volatility_penalty = 0.0
        if candidate.volatility_percent > self.config.volatility_penalty_threshold:
            volatility_penalty = min(
                15.0,
                (
                    candidate.volatility_percent
                    - self.config.volatility_penalty_threshold
                ) * 2.0,
            )

        quality = (
            score_component
            + confidence_component
            + ml_component
            + signal_component
            - volatility_penalty
        )

        return round(max(0.0, min(quality, 100.0)), 4)
