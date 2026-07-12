"""
=========================================================
BursaAI Execution Report
Version : 6.0 Sprint 6A
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from Framework.context import AnalysisContext
from Framework.execution_session import ExecutionSession


@dataclass(slots=True)
class ExecutionReport:
    session: ExecutionSession
    contexts: List[AnalysisContext] = field(default_factory=list)
    portfolio: Dict[str, Any] = field(default_factory=dict)
    queue_counts: Dict[str, int] = field(default_factory=dict)
    profiler: Dict[str, Any] = field(default_factory=dict)

    @property
    def successful(self) -> int:
        return sum(
            1 for context in self.contexts
            if not context.failed
        )

    @property
    def failed(self) -> int:
        return sum(
            1 for context in self.contexts
            if context.failed
        )

    @property
    def average_score(self) -> float:
        values = [
            context.analysis.score.final
            for context in self.contexts
        ]
        return round(sum(values) / len(values), 2) if values else 0.0

    @property
    def average_confidence(self) -> float:
        values = [
            context.analysis.confidence
            for context in self.contexts
        ]
        return round(sum(values) / len(values), 2) if values else 0.0

    def to_dict(self) -> Dict[str, Any]:
        summary = self.portfolio.get("summary", {})

        return {
            "run_id": self.session.run_id,
            "pipeline_version": self.session.pipeline_version,
            "started_at": self.session.started_at,
            "completed_at": self.session.completed_at,
            "duration_ms": round(self.session.duration_ms, 4),
            "symbols": list(self.session.symbols),
            "successful": self.successful,
            "failed": self.failed,
            "average_score": self.average_score,
            "average_confidence": self.average_confidence,
            "queue_counts": dict(self.queue_counts),
            "portfolio_summary": dict(summary),
            "profiler": dict(self.profiler),
            "warnings": list(self.session.warnings),
            "errors": list(self.session.errors),
        }
