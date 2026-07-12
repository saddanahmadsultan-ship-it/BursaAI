"""
=========================================================
BursaAI Validation Window Models
Version : 6.0 Sprint 6F.4
=========================================================
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass(slots=True)
class ValidationWindowResult:
    window_id: int
    symbol: str
    success: bool
    parameters: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    predictions: List[Any] = field(default_factory=list)
    artifacts: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ValidationRunResult:
    symbol: str
    total_windows: int
    successful_windows: int
    failed_windows: int
    results: List[ValidationWindowResult] = field(default_factory=list)
    duration_ms: float = 0.0

    @property
    def success(self) -> bool:
        return (
            self.total_windows > 0
            and self.successful_windows > 0
            and self.failed_windows == 0
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "total_windows": self.total_windows,
            "successful_windows": self.successful_windows,
            "failed_windows": self.failed_windows,
            "success": self.success,
            "duration_ms": round(self.duration_ms, 4),
            "results": [
                result.to_dict()
                for result in self.results
            ],
        }
