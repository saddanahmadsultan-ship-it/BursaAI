"""
=========================================================
BursaAI Walk Forward Analysis Report
Version : 6.0 Sprint 6F.5
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from WalkForward.analyzer_models import (
    WalkForwardAnalysisResult,
)


@dataclass(slots=True)
class WalkForwardAnalysisReport:
    result: WalkForwardAnalysisResult

    def render_text(self) -> str:
        value = self.result

        return "\n".join(
            [
                "=" * 64,
                "BURSAAI WALK FORWARD ANALYSIS REPORT",
                "=" * 64,
                f"Symbol                    : {value.symbol}",
                f"Total Windows             : {value.total_windows}",
                f"Passed Windows            : {value.passed_windows}",
                f"Failed Windows            : {value.failed_windows}",
                f"Average Training Metric   : "
                f"{value.average_training_metric:.2f}",
                f"Average Validation Metric : "
                f"{value.average_validation_metric:.2f}",
                f"Average Degradation       : "
                f"{value.average_degradation_percent:.2f}%",
                f"Stability Score           : "
                f"{value.stability_score:.2f}",
                f"Consistency Score         : "
                f"{value.consistency_score:.2f}",
                f"Robustness Score          : "
                f"{value.robustness_score:.2f}",
                f"Best Window               : {value.best_window_id}",
                f"Worst Window              : {value.worst_window_id}",
                f"Verdict                   : {value.verdict}",
                "=" * 64,
            ]
        )
