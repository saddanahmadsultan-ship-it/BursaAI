"""
=========================================================
BursaAI Walk Forward Pipeline Report
Version : 6.0 Sprint 6F.8
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from WalkForward.pipeline_models import (
    WalkForwardPipelineResult,
)


@dataclass(slots=True)
class WalkForwardPipelineReport:
    result: WalkForwardPipelineResult

    def render_text(self) -> str:
        value = self.result

        analysis = value.analysis_result
        optimization = value.optimization_result
        final_report = value.final_report

        robustness = (
            getattr(
                analysis,
                "robustness_score",
                0.0,
            )
            if analysis is not None
            else 0.0
        )

        optimization_score = 0.0

        if (
            optimization is not None
            and optimization.best_candidate is not None
        ):
            optimization_score = (
                optimization.best_candidate.optimization_score
            )

        recommendation = "UNKNOWN"

        if final_report is not None:
            recommendation = (
                final_report.summary.recommendation
            )

        return "\n".join(
            [
                "=" * 72,
                "BURSAAI WALK FORWARD PIPELINE",
                "=" * 72,
                f"Symbol                 : {value.symbol}",
                f"Strategy               : {value.strategy_name}",
                f"Status                 : "
                f"{'SUCCESS' if value.success else 'FAILED'}",
                f"Completed Stages       : {value.completed_stages}",
                f"Failed Stages          : {value.failed_stages}",
                f"Robustness             : {robustness:.2f}",
                f"Optimization Score     : {optimization_score:.2f}",
                f"Recommendation         : {recommendation}",
                f"Duration               : {value.duration_ms / 1000:.2f} sec",
                "=" * 72,
            ]
        )
