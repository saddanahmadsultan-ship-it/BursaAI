from __future__ import annotations

from TradingIntelligence.entry_engine import EntryPriceEngine
from TradingIntelligence.exit_engine import ExitLevelEngine
from TradingIntelligence.position_config import PositionIntelligenceConfig
from TradingIntelligence.position_contracts import (
    PositionCandidate,
    PositionPlan,
    PositionRiskProfile,
)
from TradingIntelligence.position_scorer import PositionQualityScorer
from TradingIntelligence.position_sizing import PositionSizingEngine
from TradingIntelligence.position_validator import PositionPlanValidator
from TradingIntelligence.risk_budget import RiskBudgetAllocator


class PositionIntelligenceEngine:
    def __init__(
        self,
        config: PositionIntelligenceConfig | None = None,
    ) -> None:
        self.config = config or PositionIntelligenceConfig()
        self.validator = PositionPlanValidator(self.config)
        self.scorer = PositionQualityScorer(self.config)
        self.risk_allocator = RiskBudgetAllocator(self.config)
        self.exit_engine = ExitLevelEngine(self.config)
        self.sizing_engine = PositionSizingEngine(self.config)

    def build_plan(
        self,
        candidate: PositionCandidate,
        profile: PositionRiskProfile,
    ) -> PositionPlan:
        eligible, validation_reasons = (
            self.validator.validate_candidate(
                candidate,
                profile,
            )
        )

        quality_score = self.scorer.score(candidate)
        entry_price = EntryPriceEngine.calculate(candidate)
        exit_levels = self.exit_engine.calculate(
            candidate,
            entry_price,
        )

        reasons = list(validation_reasons)

        if exit_levels.risk_reward < self.config.minimum_risk_reward:
            eligible = False
            reasons.append("Risk-reward ratio below minimum threshold")

        risk_percent = 0.0
        capital_at_risk = 0.0
        quantity = 0
        lot_count = 0
        position_value = 0.0

        if eligible:
            (
                risk_percent,
                capital_at_risk,
                risk_reasons,
            ) = self.risk_allocator.allocate(
                candidate,
                profile,
                quality_score,
            )
            reasons.extend(risk_reasons)

            (
                quantity,
                lot_count,
                position_value,
            ) = self.sizing_engine.calculate(
                entry_price,
                exit_levels.stop_loss,
                capital_at_risk,
                profile.available_capital,
            )

            if quantity <= 0:
                eligible = False
                reasons.append("Calculated quantity is below one tradable lot")

        position_percent = (
            position_value
            / profile.portfolio_capital
            * 100.0
            if profile.portfolio_capital > 0
            else 0.0
        )

        action = self._resolve_action(
            eligible=eligible,
            quality_score=quality_score,
            risk_reward=exit_levels.risk_reward,
            ml_probability=candidate.ml_probability,
        )

        return PositionPlan(
            symbol=candidate.symbol,
            action=action,
            approved=eligible,
            entry_price=entry_price,
            stop_loss=exit_levels.stop_loss,
            target_price=exit_levels.target_price,
            risk_reward=exit_levels.risk_reward,
            quantity=quantity,
            lot_count=lot_count,
            position_value=position_value,
            position_percent=round(position_percent, 4),
            capital_at_risk=capital_at_risk,
            risk_percent=risk_percent,
            quality_score=quality_score,
            ml_probability=round(candidate.ml_probability, 6),
            confidence=round(candidate.confidence, 4),
            signal=candidate.signal,
            reasons=reasons or ["Position plan passed all controls"],
        )

    @staticmethod
    def _resolve_action(
        eligible: bool,
        quality_score: float,
        risk_reward: float,
        ml_probability: float,
    ) -> str:
        if not eligible:
            return "REJECT_POSITION"

        if (
            quality_score >= 85.0
            and risk_reward >= 2.5
            and ml_probability >= 0.75
        ):
            return "OPEN_FULL_POSITION"

        if quality_score >= 75.0 and risk_reward >= 2.0:
            return "OPEN_STANDARD_POSITION"

        return "OPEN_REDUCED_POSITION"
