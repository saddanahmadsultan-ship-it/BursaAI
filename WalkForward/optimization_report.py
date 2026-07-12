"""
=========================================================
BursaAI Optimization Report
Version : 6.0 Sprint 6F.6C
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from WalkForward.optimization_models import (
    OptimizationCandidateResult,
    OptimizationRunResult,
)


@dataclass(slots=True)
class OptimizationReport:
    result: OptimizationRunResult
    top_n: int = 5

    def ranked_candidates(
        self,
    ) -> List[OptimizationCandidateResult]:
        successful = [
            candidate
            for candidate in self.result.candidates
            if candidate.success
        ]

        return sorted(
            successful,
            key=lambda candidate: (
                candidate.optimization_score,
                -candidate.parameter_id,
            ),
            reverse=True,
        )

    def top_candidates(
        self,
    ) -> List[OptimizationCandidateResult]:
        return self.ranked_candidates()[
            : max(int(self.top_n), 1)
        ]

    def render_text(self) -> str:
        value = self.result
        best = value.best_candidate

        lines = [
            "=" * 72,
            "BURSAAI OPTIMIZATION REPORT",
            "=" * 72,
            f"Strategy              : {value.strategy_name}",
            f"Total Candidates      : {value.total_candidates}",
            f"Completed Candidates  : {value.completed_candidates}",
            f"Failed Candidates     : {value.failed_candidates}",
            f"Duration              : {value.duration_ms:.2f} ms",
        ]

        if best is not None:
            lines.extend(
                [
                    f"Best Candidate ID     : {best.parameter_id}",
                    f"Best Score            : {best.optimization_score:.2f}",
                    f"Best Parameters       : {best.parameters}",
                ]
            )
        else:
            lines.extend(
                [
                    "Best Candidate ID     : NONE",
                    "Best Score            : 0.00",
                    "Best Parameters       : {}",
                ]
            )

        lines.extend(
            [
                "-" * 72,
                "TOP CANDIDATES",
                "-" * 72,
            ]
        )

        for rank, candidate in enumerate(
            self.top_candidates(),
            start=1,
        ):
            lines.append(
                f"{rank}. ID {candidate.parameter_id} | "
                f"Score {candidate.optimization_score:.2f} | "
                f"{candidate.parameters}"
            )

        lines.append("=" * 72)

        return "\n".join(lines)
