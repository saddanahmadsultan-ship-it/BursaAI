"""
=========================================================
BursaAI Walk Forward Final Report Builder
Version : 6.0 Sprint 6F.7
=========================================================
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from WalkForward.analyzer_models import WalkForwardAnalysisResult
from WalkForward.final_report_models import (
    WalkForwardFinalReportData,
    WalkForwardFinalSummary,
)
from WalkForward.historical_models import HistoricalRunResult
from WalkForward.optimization_models import OptimizationRunResult
from WalkForward.training_models import TrainingRunResult
from WalkForward.validation_models import ValidationRunResult


class WalkForwardFinalReportBuilder:
    def _recommendation(
        self,
        verdict: str,
        robustness_score: float,
        failed_windows: int,
    ) -> str:
        if (
            verdict == "ROBUST"
            and robustness_score >= 75
            and failed_windows == 0
        ):
            return "APPROVED FOR PAPER TRADING"

        if (
            verdict in {"ROBUST", "ACCEPTABLE"}
            and robustness_score >= 55
        ):
            return "APPROVED WITH CAUTION"

        if verdict == "WEAK":
            return "RE-OPTIMIZE"

        return "REJECT"

    def build(
        self,
        *,
        strategy_name: str,
        historical_result: HistoricalRunResult,
        training_result: TrainingRunResult,
        validation_result: ValidationRunResult,
        analysis_result: WalkForwardAnalysisResult,
        optimization_result: Optional[
            OptimizationRunResult
        ] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> WalkForwardFinalReportData:
        best_parameters = {}
        best_score = 0.0

        if (
            optimization_result is not None
            and optimization_result.best_candidate is not None
        ):
            best_parameters = dict(
                optimization_result.best_candidate.parameters
            )

            best_score = float(
                optimization_result.best_candidate.optimization_score
            )

        warnings = []

        warnings.extend(
            list(historical_result.warnings)
        )

        warnings.extend(
            list(analysis_result.warnings)
        )

        if training_result.failed_windows > 0:
            warnings.append(
                f"{training_result.failed_windows} training windows failed."
            )

        if validation_result.failed_windows > 0:
            warnings.append(
                f"{validation_result.failed_windows} validation windows failed."
            )

        recommendation = self._recommendation(
            analysis_result.verdict,
            analysis_result.robustness_score,
            analysis_result.failed_windows,
        )

        summary = WalkForwardFinalSummary(
            symbol=historical_result.symbol,
            strategy_name=str(strategy_name),
            dataset_rows=int(
                historical_result.metadata.get(
                    "dataset_rows",
                    0,
                )
            ),
            windows_generated=historical_result.windows_generated,
            training_windows=training_result.total_windows,
            validation_windows=validation_result.total_windows,
            passed_windows=analysis_result.passed_windows,
            failed_windows=analysis_result.failed_windows,
            robustness_score=analysis_result.robustness_score,
            stability_score=analysis_result.stability_score,
            consistency_score=analysis_result.consistency_score,
            average_degradation_percent=(
                analysis_result.average_degradation_percent
            ),
            best_window_id=analysis_result.best_window_id,
            worst_window_id=analysis_result.worst_window_id,
            best_parameters=best_parameters,
            best_optimization_score=best_score,
            verdict=analysis_result.verdict,
            recommendation=recommendation,
            warnings=warnings,
        )

        return WalkForwardFinalReportData(
            summary=summary,
            historical=historical_result.to_dict(),
            training=training_result.to_dict(),
            validation=validation_result.to_dict(),
            analysis=analysis_result.to_dict(),
            optimization=(
                optimization_result.to_dict()
                if optimization_result is not None
                else {}
            ),
            metadata={
                "generated_at": datetime.now(
                    timezone.utc
                ).isoformat(),
                **dict(metadata or {}),
            },
        )
