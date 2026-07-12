"""
=========================================================
BursaAI Optimization Service Registration
Version : 6.0 Sprint 6F.6B
=========================================================
"""

from __future__ import annotations

from typing import Callable, Mapping, Optional

from Framework.service_container import ServiceContainer
from WalkForward.optimization_engine import OptimizationEngine
from WalkForward.optimization_registry import OptimizationRegistry


def register_optimization_engine(
    services: ServiceContainer,
    *,
    evaluator: Callable,
    optimizer_name: str = "grid",
    weights: Optional[Mapping[str, float]] = None,
    stop_on_error: bool = False,
) -> OptimizationEngine:
    if services.contains("optimization_registry"):
        registry = services.resolve(
            "optimization_registry"
        )
    else:
        registry = OptimizationRegistry()

        services.register_instance(
            "optimization_registry",
            registry,
            replace=True,
        )

    engine = OptimizationEngine(
        evaluator=evaluator,
        services=services,
        weights=weights,
        stop_on_error=stop_on_error,
    )

    registry.register(
        optimizer_name,
        engine,
        replace=True,
    )

    services.register_instance(
        "optimization_engine",
        engine,
        replace=True,
    )

    return engine
