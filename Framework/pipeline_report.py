"""
=========================================================
BursaAI Pipeline Execution Report
Version : 6.0 Sprint 3
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from Framework.engine_result import EngineResult


@dataclass(slots=True)
class PipelineExecutionReport:
    """
    Standard summary returned after pipeline execution.
    """

    pipeline_name: str
    symbol: str
    success: bool = True
    stopped_early: bool = False
    stop_reason: str = ""
    engine_results: List[EngineResult] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    started_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    completed_at: Optional[str] = None
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    context_snapshot: Optional[Dict[str, Any]] = None

    @property
    def successful_engines(self) -> int:
        return sum(
            1
            for result in self.engine_results
            if result.success and not result.skipped
        )

    @property
    def failed_engines(self) -> int:
        return sum(
            1
            for result in self.engine_results
            if not result.success
        )

    @property
    def skipped_engines(self) -> int:
        return sum(
            1
            for result in self.engine_results
            if result.skipped
        )

    def complete(self, duration_ms: float) -> None:
        self.duration_ms = max(float(duration_ms), 0.0)
        self.completed_at = datetime.now(timezone.utc).isoformat()
        self.success = (
            self.failed_engines == 0
            and not self.errors
        )

    def add_result(self, result: EngineResult) -> None:
        self.engine_results.append(result)
        self.warnings.extend(result.warnings)
        self.errors.extend(result.errors)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pipeline_name": self.pipeline_name,
            "symbol": self.symbol,
            "success": self.success,
            "stopped_early": self.stopped_early,
            "stop_reason": self.stop_reason,
            "successful_engines": self.successful_engines,
            "failed_engines": self.failed_engines,
            "skipped_engines": self.skipped_engines,
            "duration_ms": round(self.duration_ms, 4),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "metadata": dict(self.metadata),
            "context_snapshot": self.context_snapshot,
            "engine_results": [
                result.to_dict()
                for result in self.engine_results
            ],
        }
