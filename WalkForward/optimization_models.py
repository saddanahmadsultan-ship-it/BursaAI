"""
=========================================================
BursaAI Optimization Models
Version : 6.0 Sprint 6F.6B
=========================================================
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(slots=True)
class OptimizationCandidateResult:
    parameter_id: int
    parameters: Dict[str, Any]
    success: bool
    optimization_score: float = 0.0
    metrics: Dict[str, float] = field(default_factory=dict)
    artifacts: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    duration_ms: float = 0.0
    source: str = "GRID"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class OptimizationRunResult:
    strategy_name: str
    total_candidates: int
    completed_candidates: int
    failed_candidates: int
    best_candidate: Optional[OptimizationCandidateResult] = None
    candidates: List[OptimizationCandidateResult] = field(default_factory=list)
    duration_ms: float = 0.0

    @property
    def success(self) -> bool:
        return (
            self.total_candidates > 0
            and self.completed_candidates > 0
            and self.best_candidate is not None
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy_name": self.strategy_name,
            "total_candidates": self.total_candidates,
            "completed_candidates": self.completed_candidates,
            "failed_candidates": self.failed_candidates,
            "success": self.success,
            "duration_ms": round(self.duration_ms, 4),
            "best_candidate": (
                self.best_candidate.to_dict()
                if self.best_candidate is not None
                else None
            ),
            "candidates": [
                candidate.to_dict()
                for candidate in self.candidates
            ],
        }
