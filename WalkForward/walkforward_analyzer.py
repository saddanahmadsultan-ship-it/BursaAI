"""
=========================================================
BursaAI Walk Forward Analyzer
Version : 6.0 Sprint 6F.5
=========================================================
"""

from __future__ import annotations

from typing import Dict, Iterable, Optional

from Framework.event_bus import EventBus
from Framework.exceptions import ValidationError
from Framework.service_container import ServiceContainer
from WalkForward.analyzer_metrics import (
    consistency_score,
    degradation_percent,
    robustness_score,
    safe_mean,
    stability_score,
)
from WalkForward.analyzer_models import (
    WalkForwardAnalysisResult,
    WindowAnalysis,
)
from WalkForward.training_models import (
    TrainingWindowResult,
)
from WalkForward.validation_models import (
    ValidationWindowResult,
)


class WalkForwardAnalyzer:
    """
    Compare training and validation results by window.

    Default metric names:
        training_score
        validation_score

    These may be overridden in analyze().
    """

    def __init__(
        self,
        *,
        maximum_degradation_percent: float = 30.0,
        minimum_validation_metric: float = 0.0,
        minimum_pass_rate_percent: float = 60.0,
        services: Optional[ServiceContainer] = None,
        event_bus: Optional[EventBus] = None,
    ):
        self.maximum_degradation_percent = float(
            maximum_degradation_percent
        )
        self.minimum_validation_metric = float(
            minimum_validation_metric
        )
        self.minimum_pass_rate_percent = float(
            minimum_pass_rate_percent
        )
        self.services = services

        if event_bus is not None:
            self.event_bus = event_bus
        elif (
            services is not None
            and services.contains("event_bus")
        ):
            self.event_bus = services.resolve(
                "event_bus"
            )
        else:
            self.event_bus = None

    def _verdict(
        self,
        consistency: float,
        stability: float,
        robustness: float,
    ) -> str:
        if (
            consistency >= 80
            and stability >= 75
            and robustness >= 75
        ):
            return "ROBUST"

        if (
            consistency >= 60
            and stability >= 55
            and robustness >= 55
        ):
            return "ACCEPTABLE"

        if (
            consistency >= 40
            and robustness >= 40
        ):
            return "WEAK"

        return "FAILED"

    def analyze(
        self,
        training_results: Iterable[TrainingWindowResult],
        validation_results: Iterable[ValidationWindowResult],
        *,
        training_metric_name: str = "training_score",
        validation_metric_name: str = "validation_score",
    ) -> WalkForwardAnalysisResult:
        training_items = list(training_results)
        validation_items = list(validation_results)

        if not training_items:
            raise ValidationError(
                "WalkForwardAnalyzer requires training results."
            )

        if not validation_items:
            raise ValidationError(
                "WalkForwardAnalyzer requires validation results."
            )

        training_by_window: Dict[int, TrainingWindowResult] = {
            result.window_id: result
            for result in training_items
        }

        validation_by_window: Dict[int, ValidationWindowResult] = {
            result.window_id: result
            for result in validation_items
        }

        common_windows = sorted(
            set(training_by_window)
            & set(validation_by_window)
        )

        if not common_windows:
            raise ValidationError(
                "No matching training and validation windows."
            )

        analyses = []

        for window_id in common_windows:
            training = training_by_window[
                window_id
            ]
            validation = validation_by_window[
                window_id
            ]

            notes = []

            training_metric = float(
                training.metrics.get(
                    training_metric_name,
                    0.0,
                )
            )

            validation_metric = float(
                validation.metrics.get(
                    validation_metric_name,
                    0.0,
                )
            )

            degradation = degradation_percent(
                training_metric,
                validation_metric,
            )

            passed = (
                training.success
                and validation.success
                and validation_metric
                >= self.minimum_validation_metric
                and degradation
                <= self.maximum_degradation_percent
            )

            if not training.success:
                notes.append(
                    "Training failed."
                )

            if not validation.success:
                notes.append(
                    "Validation failed."
                )

            if (
                validation_metric
                < self.minimum_validation_metric
            ):
                notes.append(
                    "Validation metric below minimum."
                )

            if (
                degradation
                > self.maximum_degradation_percent
            ):
                notes.append(
                    "Excessive out-of-sample degradation."
                )

            status = (
                "PASS"
                if passed
                else "FAIL"
            )

            analyses.append(
                WindowAnalysis(
                    window_id=window_id,
                    symbol=validation.symbol,
                    training_metric=round(
                        training_metric,
                        4,
                    ),
                    validation_metric=round(
                        validation_metric,
                        4,
                    ),
                    degradation_percent=round(
                        degradation,
                        4,
                    ),
                    passed=passed,
                    status=status,
                    notes=notes,
                )
            )

        passed_windows = sum(
            1
            for item in analyses
            if item.passed
        )

        failed_windows = (
            len(analyses)
            - passed_windows
        )

        training_values = [
            item.training_metric
            for item in analyses
        ]

        validation_values = [
            item.validation_metric
            for item in analyses
        ]

        degradation_values = [
            item.degradation_percent
            for item in analyses
        ]

        stability = stability_score(
            validation_values
        )

        consistency = consistency_score(
            passed_windows,
            len(analyses),
        )

        average_degradation = safe_mean(
            degradation_values
        )

        robustness = robustness_score(
            stability,
            consistency,
            average_degradation,
        )

        verdict = self._verdict(
            consistency,
            stability,
            robustness,
        )

        warnings = []

        if (
            consistency
            < self.minimum_pass_rate_percent
        ):
            warnings.append(
                "Walk-forward pass rate below minimum."
            )

        best = max(
            analyses,
            key=lambda item: item.validation_metric,
        )

        worst = min(
            analyses,
            key=lambda item: item.validation_metric,
        )

        result = WalkForwardAnalysisResult(
            symbol=analyses[0].symbol,
            total_windows=len(analyses),
            passed_windows=passed_windows,
            failed_windows=failed_windows,
            average_training_metric=round(
                safe_mean(training_values),
                4,
            ),
            average_validation_metric=round(
                safe_mean(validation_values),
                4,
            ),
            average_degradation_percent=round(
                average_degradation,
                4,
            ),
            stability_score=round(
                stability,
                4,
            ),
            consistency_score=round(
                consistency,
                4,
            ),
            robustness_score=round(
                robustness,
                4,
            ),
            best_window_id=best.window_id,
            worst_window_id=worst.window_id,
            verdict=verdict,
            windows=analyses,
            warnings=warnings,
        )

        if self.event_bus is not None:
            self.event_bus.publish(
                "WalkForwardAnalysisCompleted",
                payload=result.to_dict(),
                source="Walk Forward Analyzer",
            )

        return result
