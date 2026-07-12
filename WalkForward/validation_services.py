"""
=========================================================
BursaAI Validation Runner Service Registration
Version : 6.0 Sprint 6F.4
=========================================================
"""

from __future__ import annotations

from typing import Callable

from Framework.service_container import ServiceContainer
from WalkForward.validation_registry import ValidationRegistry
from WalkForward.validation_runner import ValidationWindowRunner


def register_validation_runner(
    services: ServiceContainer,
    *,
    validator: Callable,
    validator_name: str = "default",
    stop_on_error: bool = False,
) -> ValidationWindowRunner:
    if services.contains("validation_registry"):
        registry = services.resolve(
            "validation_registry"
        )
    else:
        registry = ValidationRegistry()

        services.register_instance(
            "validation_registry",
            registry,
            replace=True,
        )

    registry.register(
        validator_name,
        validator,
        replace=True,
    )

    runner = ValidationWindowRunner(
        validator=validator,
        services=services,
        stop_on_error=stop_on_error,
    )

    services.register_instance(
        "validation_window_runner",
        runner,
        replace=True,
    )

    return runner
