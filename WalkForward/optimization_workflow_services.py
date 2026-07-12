"""
=========================================================
BursaAI Optimization Workflow Service Registration
Version : 6.0 Sprint 6F.6C
=========================================================
"""

from __future__ import annotations

from Framework.service_container import (
    ServiceContainer,
)
from WalkForward.optimization_workflow import (
    OptimizationWorkflow,
)


def register_optimization_workflow(
    services: ServiceContainer,
) -> OptimizationWorkflow:
    generator = services.resolve(
        "optimization_parameter_generator"
    )

    engine = services.resolve(
        "optimization_engine"
    )

    workflow = OptimizationWorkflow(
        parameter_generator=generator,
        optimization_engine=engine,
        services=services,
    )

    services.register_instance(
        "optimization_workflow",
        workflow,
        replace=True,
    )

    return workflow
