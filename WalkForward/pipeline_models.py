"""
=========================================================
BursaAI Walk Forward Pipeline Models
Version : 6.0 Sprint 6F.8
=========================================================
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(slots=True)
class WalkForwardPipelineStage:
    name: str
    success: bool
    duration_ms: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class WalkForwardPipelineResult:
    symbol: str
    strategy_name: str
    success: bool

    historical_result: Any = None
    training_result: Any = None
    validation_result: Any = None
    analysis_result: Any = None
    optimization_result: Any = None
    final_report: Any = None

    export_paths: Dict[str, str] = field(default_factory=dict)
    stages: List[WalkForwardPipelineStage] = field(default_factory=list)
    duration_ms: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def completed_stages(self) -> int:
        return sum(1 for stage in self.stages if stage.success)

    @property
    def failed_stages(self) -> int:
        return sum(1 for stage in self.stages if not stage.success)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "strategy_name": self.strategy_name,
            "success": self.success,
            "duration_ms": round(self.duration_ms, 4),
            "completed_stages": self.completed_stages,
            "failed_stages": self.failed_stages,
            "export_paths": dict(self.export_paths),
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "stages": [stage.to_dict() for stage in self.stages],
            "historical_result": (
                self.historical_result.to_dict()
                if hasattr(self.historical_result, "to_dict")
                else self.historical_result
            ),
            "training_result": (
                self.training_result.to_dict()
                if hasattr(self.training_result, "to_dict")
                else self.training_result
            ),
            "validation_result": (
                self.validation_result.to_dict()
                if hasattr(self.validation_result, "to_dict")
                else self.validation_result
            ),
            "analysis_result": (
                self.analysis_result.to_dict()
                if hasattr(self.analysis_result, "to_dict")
                else self.analysis_result
            ),
            "optimization_result": (
                self.optimization_result.to_dict()
                if hasattr(self.optimization_result, "to_dict")
                else self.optimization_result
            ),
            "final_report": (
                self.final_report.to_dict()
                if hasattr(self.final_report, "to_dict")
                else self.final_report
            ),
        }
