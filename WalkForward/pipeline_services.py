"""
=========================================================
BursaAI Walk Forward Pipeline Service Registration
Version : 6.0 Sprint 6F.8
=========================================================
"""

from __future__ import annotations

from Framework.service_container import ServiceContainer
from WalkForward.pipeline import WalkForwardPipeline
from WalkForward.pipeline_registry import (
    WalkForwardPipelineRegistry,
)


def register_walkforward_pipeline(
    services: ServiceContainer,
    *,
    pipeline_name: str = "default",
    stop_on_error: bool = True,
) -> WalkForwardPipeline:
    historical_engine = services.resolve(
        "historical_engine"
    )

    training_runner = services.resolve(
        "training_window_runner"
    )

    validation_runner = services.resolve(
        "validation_window_runner"
    )

    analyzer = services.resolve(
        "walkforward_analyzer"
    )

    optimization_workflow = services.resolve(
        "optimization_workflow"
    )

    final_report_builder = services.resolve(
        "walkforward_final_report_builder"
    )

    final_report_exporter = services.resolve(
        "walkforward_final_report_exporter"
    )

    pipeline = WalkForwardPipeline(
        historical_engine=historical_engine,
        training_runner=training_runner,
        validation_runner=validation_runner,
        analyzer=analyzer,
        optimization_workflow=optimization_workflow,
        final_report_builder=final_report_builder,
        final_report_exporter=final_report_exporter,
        services=services,
        stop_on_error=stop_on_error,
    )

    if services.contains(
        "walkforward_pipeline_registry"
    ):
        registry = services.resolve(
            "walkforward_pipeline_registry"
        )
    else:
        registry = WalkForwardPipelineRegistry()

        services.register_instance(
            "walkforward_pipeline_registry",
            registry,
            replace=True,
        )

    registry.register(
        pipeline_name,
        pipeline,
        replace=True,
    )

    services.register_instance(
        "walkforward_pipeline",
        pipeline,
        replace=True,
    )

    return pipeline
