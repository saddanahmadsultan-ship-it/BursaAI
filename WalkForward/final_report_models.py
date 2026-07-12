"""
=========================================================
BursaAI Walk Forward Final Report Models
Version : 6.0 Sprint 6F.7
=========================================================
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(slots=True)
class WalkForwardFinalSummary:
    symbol: str
    strategy_name: str

    dataset_rows: int = 0
    windows_generated: int = 0
    training_windows: int = 0
    validation_windows: int = 0

    passed_windows: int = 0
    failed_windows: int = 0

    robustness_score: float = 0.0
    stability_score: float = 0.0
    consistency_score: float = 0.0
    average_degradation_percent: float = 0.0

    best_window_id: Optional[int] = None
    worst_window_id: Optional[int] = None

    best_parameters: Dict[str, Any] = field(default_factory=dict)
    best_optimization_score: float = 0.0

    verdict: str = "UNKNOWN"
    recommendation: str = "REVIEW"
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class WalkForwardFinalReportData:
    summary: WalkForwardFinalSummary
    historical: Dict[str, Any] = field(default_factory=dict)
    training: Dict[str, Any] = field(default_factory=dict)
    validation: Dict[str, Any] = field(default_factory=dict)
    analysis: Dict[str, Any] = field(default_factory=dict)
    optimization: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary.to_dict(),
            "historical": dict(self.historical),
            "training": dict(self.training),
            "validation": dict(self.validation),
            "analysis": dict(self.analysis),
            "optimization": dict(self.optimization),
            "metadata": dict(self.metadata),
        }
