"""
=========================================================
BursaAI Optimization Engine
Version : 6.0 Sprint 6F.6B
=========================================================
"""

from __future__ import annotations

from time import perf_counter
from typing import Any, Callable, Dict, Iterable, Mapping, Optional

from Framework.event_bus import EventBus
from Framework.exceptions import ValidationError
from Framework.service_container import ServiceContainer
from WalkForward.optimization_models import (
    OptimizationCandidateResult,
    OptimizationRunResult,
)
from WalkForward.optimization_scoring import (
    calculate_optimization_score,
)
from WalkForward.parameter_generator import GeneratedParameterSet


class OptimizationEngine:
    """
    Evaluate parameter candidates.

    Supported evaluator signatures:
        evaluator(parameters)
        evaluator(parameters, context)
        evaluator(parameter_set, context)

    Expected evaluator output:
        {
            "metrics": {...},
            "artifacts": {...},
            "warnings": [...],
            "optimization_score": optional
        }
    """

    def __init__(
        self,
        evaluator: Callable[..., Dict[str, Any]],
        *,
        services: Optional[ServiceContainer] = None,
        event_bus: Optional[EventBus] = None,
        weights: Optional[Mapping[str, float]] = None,
        stop_on_error: bool = False,
    ):
        if not callable(evaluator):
            raise ValidationError(
                "OptimizationEngine requires a callable evaluator."
            )

        self.evaluator = evaluator
        self.services = services
        self.weights = dict(weights or {})
        self.stop_on_error = bool(stop_on_error)

        if event_bus is not None:
            self.event_bus = event_bus
        elif (
            services is not None
            and services.contains("event_bus")
        ):
            self.event_bus = services.resolve("event_bus")
        else:
            self.event_bus = None

    def _call_evaluator(
        self,
        parameter_set: GeneratedParameterSet,
        context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        try:
            output = self.evaluator(
                parameter_set,
                context,
            )
        except TypeError:
            try:
                output = self.evaluator(
                    parameter_set.parameters,
                    context,
                )
            except TypeError:
                output = self.evaluator(
                    parameter_set.parameters
                )

        if output is None:
            output = {}

        if not isinstance(output, dict):
            raise ValidationError(
                "Optimization evaluator output must be a dictionary."
            )

        return output

    def evaluate_one(
        self,
        parameter_set: GeneratedParameterSet,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> OptimizationCandidateResult:
        started = perf_counter()

        try:
            output = self._call_evaluator(
                parameter_set,
                context,
            )

            metrics = {
                str(key): float(value)
                for key, value in dict(
                    output.get("metrics", {})
                ).items()
            }

            if "optimization_score" in output:
                score = float(
                    output["optimization_score"]
                )
            else:
                score = calculate_optimization_score(
                    metrics,
                    weights=(
                        self.weights
                        if self.weights
                        else None
                    ),
                )

            result = OptimizationCandidateResult(
                parameter_id=parameter_set.parameter_id,
                parameters=dict(
                    parameter_set.parameters
                ),
                success=True,
                optimization_score=round(
                    score,
                    4,
                ),
                metrics=metrics,
                artifacts=dict(
                    output.get("artifacts", {})
                ),
                warnings=[
                    str(value)
                    for value in output.get(
                        "warnings",
                        [],
                    )
                ],
                duration_ms=(
                    perf_counter() - started
                ) * 1000,
                source=parameter_set.source,
            )

        except Exception as error:
            result = OptimizationCandidateResult(
                parameter_id=parameter_set.parameter_id,
                parameters=dict(
                    parameter_set.parameters
                ),
                success=False,
                errors=[
                    f"{type(error).__name__}: {error}"
                ],
                duration_ms=(
                    perf_counter() - started
                ) * 1000,
                source=parameter_set.source,
            )

            if self.stop_on_error:
                raise

        if self.event_bus is not None:
            self.event_bus.publish(
                "OptimizationCandidateCompleted",
                payload={
                    "parameter_id": result.parameter_id,
                    "parameters": dict(result.parameters),
                    "success": result.success,
                    "optimization_score": (
                        result.optimization_score
                    ),
                    "metrics": dict(result.metrics),
                    "warnings": list(result.warnings),
                    "errors": list(result.errors),
                    "duration_ms": result.duration_ms,
                    "source": result.source,
                },
                source="Optimization Engine",
            )

        return result

    def run(
        self,
        parameter_sets: Iterable[GeneratedParameterSet],
        *,
        strategy_name: str = "default",
        context: Optional[Dict[str, Any]] = None,
    ) -> OptimizationRunResult:
        items = list(parameter_sets)

        if not items:
            raise ValidationError(
                "OptimizationEngine requires parameter sets."
            )

        started = perf_counter()

        results = [
            self.evaluate_one(
                parameter_set,
                context=context,
            )
            for parameter_set in items
        ]

        successful = [
            result
            for result in results
            if result.success
        ]

        failed = len(results) - len(successful)

        best = (
            max(
                successful,
                key=lambda result: (
                    result.optimization_score,
                    -result.parameter_id,
                ),
            )
            if successful
            else None
        )

        run_result = OptimizationRunResult(
            strategy_name=str(strategy_name),
            total_candidates=len(results),
            completed_candidates=len(successful),
            failed_candidates=failed,
            best_candidate=best,
            candidates=results,
            duration_ms=(
                perf_counter() - started
            ) * 1000,
        )

        if self.event_bus is not None:
            self.event_bus.publish(
                "OptimizationRunCompleted",
                payload=run_result.to_dict(),
                source="Optimization Engine",
            )

        return run_result
