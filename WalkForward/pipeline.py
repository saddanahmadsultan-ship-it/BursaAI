"""
=========================================================
BursaAI Full Walk Forward Pipeline
Version : 6.0 Sprint 6F.8
=========================================================
"""

from __future__ import annotations

from time import perf_counter
from typing import Any, Callable, Dict, Optional

from Framework.event_bus import EventBus
from Framework.exceptions import ValidationError
from Framework.service_container import ServiceContainer
from WalkForward.pipeline_context import WalkForwardPipelineContext
from WalkForward.pipeline_models import (
    WalkForwardPipelineResult,
    WalkForwardPipelineStage,
)


class WalkForwardPipeline:
    """
    Full flow:
        Historical
        -> Training
        -> Validation
        -> Analyzer
        -> Optimization
        -> Final Report
        -> Export
    """

    def __init__(
        self,
        *,
        historical_engine: Any,
        training_runner: Any,
        validation_runner: Any,
        analyzer: Any,
        optimization_workflow: Any,
        final_report_builder: Any,
        final_report_exporter: Any,
        services: Optional[ServiceContainer] = None,
        event_bus: Optional[EventBus] = None,
        stop_on_error: bool = True,
    ):
        self.historical_engine = historical_engine
        self.training_runner = training_runner
        self.validation_runner = validation_runner
        self.analyzer = analyzer
        self.optimization_workflow = optimization_workflow
        self.final_report_builder = final_report_builder
        self.final_report_exporter = final_report_exporter
        self.services = services
        self.stop_on_error = bool(stop_on_error)

        if event_bus is not None:
            self.event_bus = event_bus
        elif services is not None and services.contains("event_bus"):
            self.event_bus = services.resolve("event_bus")
        else:
            self.event_bus = None

    def _publish(
        self,
        name: str,
        payload: Dict[str, Any],
    ) -> None:
        if self.event_bus is not None:
            self.event_bus.publish(
                name,
                payload=payload,
                source="Walk Forward Pipeline",
            )

    def _run_stage(
        self,
        stages,
        stage_name: str,
        function: Callable[[], Any],
    ) -> Any:
        started = perf_counter()

        try:
            output = function()

            stage = WalkForwardPipelineStage(
                name=stage_name,
                success=True,
                duration_ms=(perf_counter() - started) * 1000,
            )

            stages.append(stage)

            self._publish(
                f"WalkForward{stage_name}Completed",
                {
                    "stage": stage_name,
                    "success": True,
                    "duration_ms": stage.duration_ms,
                },
            )

            return output

        except Exception as error:
            stage = WalkForwardPipelineStage(
                name=stage_name,
                success=False,
                duration_ms=(perf_counter() - started) * 1000,
                error=f"{type(error).__name__}: {error}",
            )

            stages.append(stage)

            self._publish(
                "WalkForwardPipelineFailed",
                {
                    "stage": stage_name,
                    "error": stage.error,
                },
            )

            if self.stop_on_error:
                raise

            return None

    def run(
        self,
        symbol: str,
        *,
        strategy_name: str,
        config: Any = None,
        training_context: Optional[Dict[str, Any]] = None,
        validation_context: Optional[Dict[str, Any]] = None,
        optimization_context: Optional[Dict[str, Any]] = None,
        training_metric_name: str = "training_score",
        validation_metric_name: str = "validation_score",
        optimization_mode: str = "grid",
        random_count: int = 10,
        export_report: bool = True,
        output_directory: str = "Reports/WalkForward",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> WalkForwardPipelineResult:
        symbol = str(symbol).strip()
        strategy_name = str(strategy_name).strip()

        if not symbol:
            raise ValidationError(
                "Walk Forward Pipeline requires a symbol."
            )

        if not strategy_name:
            raise ValidationError(
                "Walk Forward Pipeline requires a strategy name."
            )

        started = perf_counter()
        stages = []
        context = WalkForwardPipelineContext(
            symbol=symbol,
            strategy_name=strategy_name,
            config=config,
            metadata=dict(metadata or {}),
        )

        self._publish(
            "WalkForwardPipelineStarted",
            {
                "symbol": symbol,
                "strategy_name": strategy_name,
            },
        )

        errors = []
        warnings = []

        try:
            context.current_stage = "Historical"

            context.historical_result = self._run_stage(
                stages,
                "Historical",
                lambda: self.historical_engine.run(
                    symbol,
                    config=config,
                ),
            )

            if context.historical_result is None:
                raise ValidationError(
                    "Historical stage produced no result."
                )

            warnings.extend(
                list(
                    getattr(
                        context.historical_result,
                        "warnings",
                        [],
                    )
                )
            )

            splits = context.historical_result.splits

            context.current_stage = "Training"

            context.training_result = self._run_stage(
                stages,
                "Training",
                lambda: self.training_runner.run_many(
                    splits,
                    context=training_context,
                ),
            )

            context.current_stage = "Validation"

            context.validation_result = self._run_stage(
                stages,
                "Validation",
                lambda: self.validation_runner.run_many(
                    splits,
                    context.training_result.results,
                    context=validation_context,
                ),
            )

            context.current_stage = "Analysis"

            context.analysis_result = self._run_stage(
                stages,
                "Analysis",
                lambda: self.analyzer.analyze(
                    context.training_result.results,
                    context.validation_result.results,
                    training_metric_name=training_metric_name,
                    validation_metric_name=validation_metric_name,
                ),
            )

            warnings.extend(
                list(
                    getattr(
                        context.analysis_result,
                        "warnings",
                        [],
                    )
                )
            )

            context.current_stage = "Optimization"

            if optimization_mode.lower() == "random":
                context.optimization_result = self._run_stage(
                    stages,
                    "Optimization",
                    lambda: self.optimization_workflow.run_random(
                        random_count,
                        strategy_name=strategy_name,
                        context=optimization_context,
                    ).run_result,
                )
            else:
                context.optimization_result = self._run_stage(
                    stages,
                    "Optimization",
                    lambda: self.optimization_workflow.run_grid(
                        strategy_name=strategy_name,
                        context=optimization_context,
                    ).run_result,
                )

            context.current_stage = "Report"

            context.final_report = self._run_stage(
                stages,
                "Report",
                lambda: self.final_report_builder.build(
                    strategy_name=strategy_name,
                    historical_result=context.historical_result,
                    training_result=context.training_result,
                    validation_result=context.validation_result,
                    analysis_result=context.analysis_result,
                    optimization_result=context.optimization_result,
                    metadata=context.metadata,
                ),
            )

            if export_report:
                context.current_stage = "Export"

                context.export_paths = self._run_stage(
                    stages,
                    "Export",
                    lambda: self.final_report_exporter.export(
                        context.final_report,
                        output_directory=output_directory,
                    ),
                )

            context.current_stage = "COMPLETED"

        except Exception as error:
            context.failed = True
            context.error = f"{type(error).__name__}: {error}"
            errors.append(context.error)

        success = (
            not context.failed
            and all(stage.success for stage in stages)
            and context.final_report is not None
        )

        result = WalkForwardPipelineResult(
            symbol=symbol,
            strategy_name=strategy_name,
            success=success,
            historical_result=context.historical_result,
            training_result=context.training_result,
            validation_result=context.validation_result,
            analysis_result=context.analysis_result,
            optimization_result=context.optimization_result,
            final_report=context.final_report,
            export_paths=dict(context.export_paths),
            stages=stages,
            duration_ms=(perf_counter() - started) * 1000,
            errors=errors,
            warnings=warnings,
        )

        self._publish(
            "WalkForwardPipelineCompleted",
            result.to_dict(),
        )

        return result
