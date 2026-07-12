"""
=========================================================
BursaAI Full Analysis Pipeline Factory
Version : 6.0 Sprint 5A.4
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from Framework.engine_registry import EngineRegistry
from Framework.event_audit import EventAuditTrail
from Framework.infrastructure import InfrastructureBundle
from Framework.logger import FrameworkLogger
from Framework.pipeline import Pipeline
from Framework.pipeline_policy import PipelinePolicy
from Framework.profiler import EngineProfiler


@dataclass(slots=True)
class FullPipelineBundle:
    registry: EngineRegistry
    pipeline: Pipeline
    logger: FrameworkLogger
    profiler: EngineProfiler
    audit: EventAuditTrail


def build_full_pipeline(
    infrastructure: InfrastructureBundle,
    *,
    name: str = "BursaAI Full Analysis Pipeline",
    failure_mode: str = "stop",
    echo_logs: bool = False,
    record_context_snapshot: bool = True,
) -> FullPipelineBundle:
    """
    Build registry, logger, profiler, event audit and pipeline.
    Adapters are registered separately by
    register_full_analysis_pipeline().
    """

    logger = FrameworkLogger(
        echo=echo_logs
    )

    profiler = EngineProfiler()

    registry = EngineRegistry(
        logger=logger,
        profiler=profiler,
    )

    audit = EventAuditTrail()
    audit.attach(
        infrastructure.events
    )

    pipeline = Pipeline(
        name=name,
        registry=registry,
        policy=PipelinePolicy(
            failure_mode=failure_mode,
            validate_dependencies=True,
            record_context_snapshot=record_context_snapshot,
        ),
        logger=logger,
        profiler=profiler,
    )

    infrastructure.services.register_instance(
        "engine_registry",
        registry,
        replace=True,
    )

    infrastructure.services.register_instance(
        "pipeline",
        pipeline,
        replace=True,
    )

    infrastructure.services.register_instance(
        "framework_logger",
        logger,
        replace=True,
    )

    infrastructure.services.register_instance(
        "engine_profiler",
        profiler,
        replace=True,
    )

    infrastructure.services.register_instance(
        "event_audit",
        audit,
        replace=True,
    )

    return FullPipelineBundle(
        registry=registry,
        pipeline=pipeline,
        logger=logger,
        profiler=profiler,
        audit=audit,
    )
