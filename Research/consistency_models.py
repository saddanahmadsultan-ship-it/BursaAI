from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict


@dataclass
class ConsistencyBreakdown:
    fold_consistency_score: float = 0.0
    monthly_stability_score: float = 0.0
    yearly_stability_score: float = 0.0
    equity_smoothness_score: float = 0.0
    return_reliability_score: float = 0.0
    overall_consistency_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
