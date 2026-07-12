"""
=========================================================
BursaAI Domain Models
Version : 6.0 Sprint 1
=========================================================
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from Framework.exceptions import ValidationError


def _clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(float(value), maximum))


@dataclass(slots=True)
class IdentityModel:
    code: str = ""
    name: str = ""
    sector: str = ""
    price: float = 0.0
    currency: str = "MYR"

    def validate(self) -> None:
        if not self.code:
            raise ValidationError("Stock code is required.")

        if self.price < 0:
            raise ValidationError("Stock price cannot be negative.")


@dataclass(slots=True)
class ScoreModel:
    raw: float = 0.0
    quality_penalty: float = 0.0
    tradeable: float = 0.0
    institution_bonus: float = 0.0
    regime_bonus: float = 0.0
    regime_penalty: float = 0.0
    final: float = 0.0
    grade: str = "F"

    def normalize(self) -> None:
        self.raw = _clamp(self.raw)
        self.quality_penalty = max(float(self.quality_penalty), 0.0)
        self.tradeable = _clamp(self.tradeable)
        self.institution_bonus = max(float(self.institution_bonus), 0.0)
        self.regime_bonus = max(float(self.regime_bonus), 0.0)
        self.regime_penalty = max(float(self.regime_penalty), 0.0)
        self.final = _clamp(self.final)


@dataclass(slots=True)
class MarketModel:
    trend: str = "UNKNOWN"
    momentum: str = "UNKNOWN"
    volume: str = "UNKNOWN"
    smart_money: str = "NONE"
    regime: str = "UNKNOWN"
    regime_score: float = 0.0
    volatility: str = "UNKNOWN"
    mtf_alignment_score: float = 50.0
    mtf_status: str = "NEUTRAL"

    def normalize(self) -> None:
        self.regime_score = max(-100.0, min(float(self.regime_score), 100.0))
        self.mtf_alignment_score = _clamp(self.mtf_alignment_score)


@dataclass(slots=True)
class TradeModel:
    signal: str = "UNKNOWN"
    decision_signal: str = "UNKNOWN"
    rating: str = "UNKNOWN"
    entry: float = 0.0
    stop_loss: float = 0.0
    target: float = 0.0
    risk_reward: float = 0.0

    def validate(self) -> None:
        for label, value in (
            ("entry", self.entry),
            ("stop_loss", self.stop_loss),
            ("target", self.target),
            ("risk_reward", self.risk_reward),
        ):
            if value < 0:
                raise ValidationError(f"Trade {label} cannot be negative.")


@dataclass(slots=True)
class TimingModel:
    score: float = 0.0
    status: str = "UNKNOWN"
    action: str = "NO ACTION"
    entry_zone_low: float = 0.0
    entry_zone_high: float = 0.0
    reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def normalize(self) -> None:
        self.score = _clamp(self.score)
        self.entry_zone_low = max(float(self.entry_zone_low), 0.0)
        self.entry_zone_high = max(float(self.entry_zone_high), 0.0)


@dataclass(slots=True)
class AIBrainModel:
    conviction_score: float = 0.0
    conviction_level: str = "NO CONVICTION"
    signal: str = "AVOID"
    prediction_stability: float = 0.0
    execution_quality: float = 0.0
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    summary: str = ""
    components: Dict[str, float] = field(default_factory=dict)
    contributions: Dict[str, float] = field(default_factory=dict)

    def normalize(self) -> None:
        self.conviction_score = _clamp(self.conviction_score)
        self.prediction_stability = _clamp(self.prediction_stability)
        self.execution_quality = _clamp(self.execution_quality)
        self.components = {
            key: _clamp(value)
            for key, value in self.components.items()
        }


@dataclass(slots=True)
class PositionModel:
    account_capital: float = 0.0
    risk_percent: float = 0.0
    risk_capital: float = 0.0
    risk_per_share: float = 0.0
    shares: int = 0
    lots: int = 0
    capital_used: float = 0.0
    remaining_capital: float = 0.0
    allocation_percent: float = 0.0
    actual_risk_percent: float = 0.0
    max_loss: float = 0.0
    potential_profit: float = 0.0
    status: str = "PENDING"
    rating: str = "NONE"

    def validate(self) -> None:
        numeric_values = (
            self.account_capital,
            self.risk_percent,
            self.risk_capital,
            self.risk_per_share,
            self.capital_used,
            self.remaining_capital,
            self.allocation_percent,
            self.actual_risk_percent,
            self.max_loss,
            self.potential_profit,
        )

        if any(value < 0 for value in numeric_values):
            raise ValidationError("Position values cannot be negative.")

        if self.shares < 0 or self.lots < 0:
            raise ValidationError("Position shares and lots cannot be negative.")

        tolerance = 0.01
        if self.capital_used > self.account_capital + tolerance:
            raise ValidationError(
                "Position capital used exceeds account capital."
            )


@dataclass(slots=True)
class PortfolioModel:
    eligible: bool = False
    rank: Optional[int] = None
    status: str = "PENDING"
    reason: str = ""
    suggested_shares: int = 0
    suggested_lots: int = 0
    suggested_capital: float = 0.0
    suggested_max_loss: float = 0.0
    allocated_shares: int = 0
    allocated_lots: int = 0
    allocated_capital: float = 0.0
    allocated_max_loss: float = 0.0
    allocated_potential_profit: float = 0.0
    allocation_percent: float = 0.0
    risk_percent: float = 0.0
    remaining_cash_after: float = 0.0

    def validate(self) -> None:
        numeric_values = (
            self.suggested_capital,
            self.suggested_max_loss,
            self.allocated_capital,
            self.allocated_max_loss,
            self.allocated_potential_profit,
            self.allocation_percent,
            self.risk_percent,
            self.remaining_cash_after,
        )

        if any(value < 0 for value in numeric_values):
            raise ValidationError("Portfolio values cannot be negative.")

        if (
            self.suggested_shares < 0
            or self.suggested_lots < 0
            or self.allocated_shares < 0
            or self.allocated_lots < 0
        ):
            raise ValidationError(
                "Portfolio shares and lots cannot be negative."
            )


@dataclass(slots=True)
class AnalysisModel:
    identity: IdentityModel = field(default_factory=IdentityModel)
    score: ScoreModel = field(default_factory=ScoreModel)
    confidence: float = 0.0
    confidence_level: str = "UNKNOWN"
    market: MarketModel = field(default_factory=MarketModel)
    trade: TradeModel = field(default_factory=TradeModel)
    timing: TimingModel = field(default_factory=TimingModel)
    ai: AIBrainModel = field(default_factory=AIBrainModel)
    position: PositionModel = field(default_factory=PositionModel)
    portfolio: PortfolioModel = field(default_factory=PortfolioModel)
    reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    summary: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)

    def normalize(self) -> None:
        self.score.normalize()
        self.market.normalize()
        self.timing.normalize()
        self.ai.normalize()
        self.confidence = _clamp(self.confidence)

    def validate(self) -> None:
        self.normalize()
        self.identity.validate()
        self.trade.validate()
        self.position.validate()
        self.portfolio.validate()

    def to_dict(self) -> Dict[str, Any]:
        self.validate()
        return asdict(self)
