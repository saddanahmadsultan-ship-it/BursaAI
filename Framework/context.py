"""
=========================================================
BursaAI Analysis Context
Version : 6.0 Sprint 1
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from Framework.domain import AnalysisModel
from Framework.engine_result import EngineResult
from Framework.exceptions import ValidationError


@dataclass
class AnalysisContext:
    """
    Shared object that will move through the future BursaAI pipeline.
    """

    symbol: str
    data: Any = None
    indicators: Any = None
    analysis: AnalysisModel = field(default_factory=AnalysisModel)
    engine_results: Dict[str, EngineResult] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    started_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    completed_at: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.symbol or not self.symbol.strip():
            raise ValidationError("AnalysisContext requires a symbol.")

        if not self.analysis.identity.code:
            self.analysis.identity.code = self.symbol

    @property
    def failed(self) -> bool:
        return bool(self.errors)

    @property
    def successful_engines(self) -> int:
        return sum(
            1
            for result in self.engine_results.values()
            if result.success and not result.skipped
        )

    @property
    def failed_engines(self) -> int:
        return sum(
            1
            for result in self.engine_results.values()
            if not result.success
        )

    def add_result(self, result: EngineResult) -> None:
        result.validate()
        self.engine_results[result.engine] = result

        self.warnings.extend(result.warnings)
        self.errors.extend(result.errors)

    def add_log(self, message: str) -> None:
        self.logs.append(str(message))

    def add_warning(self, message: str) -> None:
        self.warnings.append(str(message))

    def add_error(self, message: str) -> None:
        self.errors.append(str(message))

    def complete(self) -> None:
        self.completed_at = datetime.now(timezone.utc).isoformat()

    def validate(self) -> None:
        if not self.symbol:
            raise ValidationError("Context symbol cannot be empty.")

        self.analysis.validate()

    def summary(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "failed": self.failed,
            "successful_engines": self.successful_engines,
            "failed_engines": self.failed_engines,
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "metadata": dict(self.metadata),
        }

    def to_legacy_dict(self) -> Dict[str, Any]:
        """
        Temporary bridge for legacy BursaAI modules.

        Sprint 1 does not replace the existing result_model.py.
        This method provides common flat aliases when adapters are added.
        """

        self.analysis.validate()

        analysis = self.analysis

        return {
            "Code": analysis.identity.code,
            "Price": analysis.identity.price,
            "RawScore": analysis.score.raw,
            "QualityPenalty": analysis.score.quality_penalty,
            "TradeableScore": analysis.score.tradeable,
            "InstitutionBonus": analysis.score.institution_bonus,
            "RegimeBonus": analysis.score.regime_bonus,
            "RegimePenalty": analysis.score.regime_penalty,
            "FinalScore": analysis.score.final,
            "Grade": analysis.score.grade,
            "Confidence": analysis.confidence,
            "ConfLevel": analysis.confidence_level,
            "Trend": analysis.market.trend,
            "Volume": analysis.market.volume,
            "SmartMoney": analysis.market.smart_money,
            "MarketRegime": analysis.market.regime,
            "RegimeScore": analysis.market.regime_score,
            "Signal": analysis.trade.signal,
            "DecisionSignal": analysis.trade.decision_signal,
            "Rating": analysis.trade.rating,
            "Entry": analysis.trade.entry,
            "StopLoss": analysis.trade.stop_loss,
            "Target": analysis.trade.target,
            "RR": analysis.trade.risk_reward,
            "EntryTimingScore": analysis.timing.score,
            "EntryTimingStatus": analysis.timing.status,
            "EntryTimingAction": analysis.timing.action,
            "AIConviction": analysis.ai.conviction_score,
            "AIConvictionLevel": analysis.ai.conviction_level,
            "AISignal": analysis.ai.signal,
            "AccountCapital": analysis.position.account_capital,
            "RiskPercent": analysis.position.risk_percent,
            "RiskCapital": analysis.position.risk_capital,
            "RiskPerShare": analysis.position.risk_per_share,
            "Shares": analysis.position.shares,
            "Lots": analysis.position.lots,
            "CapitalUsed": analysis.position.capital_used,
            "RemainingCapital": analysis.position.remaining_capital,
            "Allocation": analysis.position.allocation_percent,
            "ActualRiskPercent": analysis.position.actual_risk_percent,
            "MaxLoss": analysis.position.max_loss,
            "PotentialProfit": analysis.position.potential_profit,
            "PositionStatus": analysis.position.status,
            "PositionRating": analysis.position.rating,
            "PortfolioEligible": analysis.portfolio.eligible,
            "PortfolioRank": analysis.portfolio.rank,
            "PortfolioStatus": analysis.portfolio.status,
            "PortfolioReason": analysis.portfolio.reason,
            "AllocatedShares": analysis.portfolio.allocated_shares,
            "AllocatedLots": analysis.portfolio.allocated_lots,
            "AllocatedCapital": analysis.portfolio.allocated_capital,
            "AllocatedMaxLoss": analysis.portfolio.allocated_max_loss,
            "AllocatedPotentialProfit": (
                analysis.portfolio.allocated_potential_profit
            ),
            "PortfolioAllocation": analysis.portfolio.allocation_percent,
            "PortfolioRiskPercent": analysis.portfolio.risk_percent,
            "PortfolioRemainingCash": (
                analysis.portfolio.remaining_cash_after
            ),
            "Summary": analysis.summary,
            "Reason": list(analysis.reasons),
            "Warning": list(analysis.warnings),
        }
