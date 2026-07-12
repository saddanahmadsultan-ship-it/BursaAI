"""
=========================================================
BursaAI Walk Forward Final Report Renderer
Version : 6.0 Sprint 6F.7
=========================================================
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from WalkForward.final_report_models import (
    WalkForwardFinalReportData,
)


@dataclass(slots=True)
class WalkForwardFinalReportRenderer:
    report: WalkForwardFinalReportData

    def render_text(self) -> str:
        value = self.report.summary

        lines = [
            "=" * 76,
            "BURSAAI WALK FORWARD FINAL REPORT",
            "=" * 76,
            f"Symbol                    : {value.symbol}",
            f"Strategy                  : {value.strategy_name}",
            f"Dataset Rows              : {value.dataset_rows}",
            f"Windows Generated         : {value.windows_generated}",
            f"Training Windows          : {value.training_windows}",
            f"Validation Windows        : {value.validation_windows}",
            f"Passed Windows            : {value.passed_windows}",
            f"Failed Windows            : {value.failed_windows}",
            f"Robustness Score          : {value.robustness_score:.2f}",
            f"Stability Score           : {value.stability_score:.2f}",
            f"Consistency Score         : {value.consistency_score:.2f}",
            f"Average Degradation       : "
            f"{value.average_degradation_percent:.2f}%",
            f"Best Window               : {value.best_window_id}",
            f"Worst Window              : {value.worst_window_id}",
            f"Best Optimization Score   : "
            f"{value.best_optimization_score:.2f}",
            f"Best Parameters           : {value.best_parameters}",
            f"Verdict                   : {value.verdict}",
            f"Recommendation            : {value.recommendation}",
        ]

        if value.warnings:
            lines.extend(
                [
                    "-" * 76,
                    "WARNINGS",
                    "-" * 76,
                ]
            )

            for warning in value.warnings:
                lines.append(
                    f"- {warning}"
                )

        lines.append("=" * 76)

        return "\n".join(lines)

    def render_json(
        self,
        *,
        indent: int = 2,
    ) -> str:
        return json.dumps(
            self.report.to_dict(),
            indent=indent,
            ensure_ascii=False,
            default=str,
        )
