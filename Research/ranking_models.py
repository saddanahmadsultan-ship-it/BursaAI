from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from Research.robustness_models import RobustnessBreakdown


@dataclass
class RankingBreakdown:
    performance_score: float = 0.0
    risk_score: float = 0.0
    consistency_score: float = 0.0
    robustness_score: float = 0.0
    confidence_score: float = 0.0
    overall_score: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


@dataclass
class RankedStrategy:
    rank: int
    result_id: str
    experiment_id: str
    candidate_id: str
    candidate_hash: str
    strategy_name: str
    candidate_name: str
    parameters: Dict[str, Any]
    breakdown: RankingBreakdown
    tier: str
    recommendation: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    robustness_breakdown: Optional[RobustnessBreakdown] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["breakdown"] = self.breakdown.to_dict()

        if self.robustness_breakdown is not None:
            data["robustness_breakdown"] = (
                self.robustness_breakdown.to_dict()
            )

        return data
