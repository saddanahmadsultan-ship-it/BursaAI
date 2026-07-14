from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict


@dataclass
class RobustnessBreakdown:
    fold_success_score: float = 0.0
    degradation_score: float = 0.0
    fold_dispersion_score: float = 0.0
    parameter_stability_score: float = 0.0
    regime_stability_score: float = 0.0
    overall_robustness_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
