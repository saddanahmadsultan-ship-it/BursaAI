"""
=========================================================
BursaAI Validation Window Runner
Version : 6.0 Sprint 6F.4
=========================================================
"""

from __future__ import annotations

from time import perf_counter
from typing import Any, Callable, Dict, Iterable, Mapping, Optional

from Framework.event_bus import EventBus
from Framework.exceptions import ValidationError
from Framework.service_container import ServiceContainer
from WalkForward.dataset_splitter import DatasetSplit
from WalkForward.training_models import TrainingWindowResult
from WalkForward.validation_models import (
    ValidationRunResult,
    ValidationWindowResult,
)


class ValidationWindowRunner:
    """
    Runs out-of-sample validation using parameters from training.

    Supported validator signatures:
        validator(validation_data, parameters)
        validator(validation_data, parameters, split)
        validator(validation_data, parameters, split, context)

    Expected output:
        {
            "metrics": {...},
            "predictions": [...],
            "artifacts": {...},
            "warnings": [...]
        }
    """

    def __init__(
        self,
        validator: Callable[..., Dict[str, Any]],
        *,
        services: Optional[ServiceContainer] = None,
        event_bus: Optional[EventBus] = None,
        stop_on_error: bool = False,
    ):
        if not callable(validator):
            raise ValidationError(
                "ValidationWindowRunner requires a callable validator."
            )

        self.validator = validator
        self.services = services
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

    def _call_validator(
        self,
        split: DatasetSplit,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        data = split.validation.data

        try:
            output = self.validator(
                data,
                parameters,
                split,
                context,
            )
        except TypeError:
            try:
                output = self.validator(
                    data,
                    parameters,
                    split,
                )
            except TypeError:
                output = self.validator(
                    data,
                    parameters,
                )

        if output is None:
            output = {}

        if not isinstance(output, dict):
            raise ValidationError(
                "Validator output must be a dictionary."
            )

        return output

    def run_one(
        self,
        split: DatasetSplit,
        training_result: TrainingWindowResult,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> ValidationWindowResult:
        split.validate()

        if training_result.window_id != split.window_id:
            raise ValidationError(
                "Training result and validation split window ids differ."
            )

        if not training_result.success:
            raise ValidationError(
                f"Training window {split.window_id} was not successful."
            )

        started = perf_counter()

        try:
            output = self._call_validator(
                split,
                dict(training_result.parameters),
                context,
            )

            result = ValidationWindowResult(
                window_id=split.window_id,
                symbol=split.validation.symbol,
                success=True,
                parameters=dict(training_result.parameters),
                metrics={
                    str(key): float(value)
                    for key, value in dict(
                        output.get("metrics", {})
                    ).items()
                },
                predictions=list(
                    output.get("predictions", [])
                ),
                artifacts=dict(
                    output.get("artifacts", {})
                ),
                warnings=[
                    str(value)
                    for value in output.get("warnings", [])
                ],
                duration_ms=(
                    perf_counter() - started
                ) * 1000,
            )

        except Exception as error:
            result = ValidationWindowResult(
                window_id=split.window_id,
                symbol=split.validation.symbol,
                success=False,
                parameters=dict(training_result.parameters),
                errors=[
                    f"{type(error).__name__}: {error}"
                ],
                duration_ms=(
                    perf_counter() - started
                ) * 1000,
            )

            if self.stop_on_error:
                raise

        if self.event_bus is not None:
            self.event_bus.publish(
                "ValidationWindowCompleted",
                payload={
                    "window_id": result.window_id,
                    "symbol": result.symbol,
                    "success": result.success,
                    "parameters": dict(result.parameters),
                    "metrics": dict(result.metrics),
                    "warnings": list(result.warnings),
                    "errors": list(result.errors),
                    "duration_ms": result.duration_ms,
                },
                source="Validation Window Runner",
            )

        return result

    def run_many(
        self,
        splits: Iterable[DatasetSplit],
        training_results: Iterable[TrainingWindowResult],
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> ValidationRunResult:
        split_items = list(splits)
        training_items = list(training_results)

        if not split_items:
            raise ValidationError(
                "Validation runner requires at least one dataset split."
            )

        training_by_window = {
            result.window_id: result
            for result in training_items
        }

        started = perf_counter()
        results = []

        for split in split_items:
            training_result = training_by_window.get(
                split.window_id
            )

            if training_result is None:
                if self.stop_on_error:
                    raise ValidationError(
                        f"No training result for window {split.window_id}."
                    )

                results.append(
                    ValidationWindowResult(
                        window_id=split.window_id,
                        symbol=split.validation.symbol,
                        success=False,
                        errors=[
                            f"No training result for window {split.window_id}."
                        ],
                    )
                )
                continue

            results.append(
                self.run_one(
                    split,
                    training_result,
                    context=context,
                )
            )

        successful = sum(
            1
            for result in results
            if result.success
        )

        failed = len(results) - successful

        run_result = ValidationRunResult(
            symbol=split_items[0].validation.symbol,
            total_windows=len(results),
            successful_windows=successful,
            failed_windows=failed,
            results=results,
            duration_ms=(
                perf_counter() - started
            ) * 1000,
        )

        if self.event_bus is not None:
            self.event_bus.publish(
                "ValidationRunCompleted",
                payload=run_result.to_dict(),
                source="Validation Window Runner",
            )

        return run_result
