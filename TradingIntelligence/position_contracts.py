from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class PositionRiskProfile:
    portfolio_capital: float
    available_capital: float
    current_portfolio_risk_percent: float = 0.0
    active_positions: int = 0
    current_drawdown_percent: float = 0.0
    sector_exposure_percent: float = 0.0


@dataclass
class PositionCandidate:
    symbol: str
    price: float
    atr: float
    final_score: float
    confidence: float
    signal: str
    ml_probability: float = 0.50
    volatility_percent: float = 0.0
    sector: str = "UNKNOWN"
    support_price: float | None = None
    resistance_price: float | None = None
    preferred_entry: float | None = None


@dataclass
class PositionDecision:
    action: str
    approved: bool
    quality_score: float
    risk_multiplier: float
    reasons: List[str] = field(default_factory=list)


@dataclass
class PositionPlan:
    symbol: str
    action: str
    approved: bool
    entry_price: float
    stop_loss: float
    target_price: float
    risk_reward: float
    quantity: int
    lot_count: int
    position_value: float
    position_percent: float
    capital_at_risk: float
    risk_percent: float
    quality_score: float
    ml_probability: float
    confidence: float
    signal: str
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
