from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class PositionIntelligenceConfig:
    portfolio_capital: float = 100000.0
    base_risk_percent: float = 1.0
    minimum_risk_percent: float = 0.25
    maximum_risk_percent: float = 1.50
    maximum_position_percent: float = 25.0
    minimum_position_percent: float = 2.0
    cash_reserve_percent: float = 10.0
    maximum_active_positions: int = 5
    minimum_confidence: float = 65.0
    minimum_final_score: float = 65.0
    minimum_ml_probability: float = 0.55
    minimum_risk_reward: float = 1.50
    target_risk_reward: float = 2.50
    atr_stop_multiplier: float = 1.50
    atr_target_multiplier: float = 3.00
    lot_size: int = 100
    round_lot: bool = True
    maximum_sector_exposure_percent: float = 35.0
    volatility_penalty_threshold: float = 3.5
    drawdown_guard_percent: float = 8.0
    signal_risk_multiplier: Dict[str, float] = field(
        default_factory=lambda: {
            "STRONG CONVICTION BUY": 1.20,
            "STRONG BUY": 1.00,
            "BUY": 0.85,
            "ACCUMULATE": 0.75,
            "WATCH": 0.40,
            "HOLD": 0.00,
            "AVOID": 0.00,
            "UNKNOWN": 0.00,
        }
    )
