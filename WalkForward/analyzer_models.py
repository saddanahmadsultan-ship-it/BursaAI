"""
=========================================================
BursaAI Walk Forward Analyzer Models
Version : 6.0 Sprint 6F.5
=========================================================
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional


@dataclass(slots=True)
class WindowAnalysis:
    window_id: int
    symbol: str
    training_metric: float = 0.0
    validation_metric: float = 0.0
    degradation_percent: float = 0.0
    passed: bool = False
    status: str = "UNKNOWN"
    notes: List[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


@dataclass(slots=True)
class WalkForwardAnalysisResult:
    symbol: str
    total_windows: int
    passed_windows: int
    failed_windows: int

    average_training_metric: float = 0.0
    average_validation_metric: float = 0.0
    average_degradation_percent: float = 0.0

    stability_score: float = 0.0
    consistency_score: float = 0.0
    robustness_score: float = 0.0

    best_window_id: Optional[int] = None
    worst_window_id: Optional[int] = None

    verdict: str = "UNKNOWN"
    windows: List[WindowAnalysis] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return (
            self.total_windows > 0
            and self.passed_windows > 0
            and self.verdict not in {"FAILED", "UNKNOWN"}
        )

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "total_windows": self.total_windows,
            "passed_windows": self.passed_windows,
            "failed_windows": self.failed_windows,
            "average_training_metric": self.average_training_metric,
            "average_validation_metric": self.average_validation_metric,
            "average_degradation_percent": self.average_degradation_percent,
            "stability_score": self.stability_score,
            "consistency_score": self.consistency_score,
            "robustness_score": self.robustness_score,
            "best_window_id": self.best_window_id,
            "worst_window_id": self.worst_window_id,
            "verdict": self.verdict,
            "success": self.success,
            "warnings": list(self.warnings),
            "windows": [
                window.to_dict()
                for window in self.windows
            ],
        }
