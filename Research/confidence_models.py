from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict


@dataclass
class ConfidenceBreakdown:
    data_coverage_score: float = 0.0
    fold_quality_score: float = 0.0
    trade_sample_score: float = 0.0
    regime_coverage_score: float = 0.0
    stability_alignment_score: float = 0.0
    out_of_sample_quality_score: float = 0.0
    overall_confidence_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
