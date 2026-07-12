"""
=========================================================
BursaAI Parameter Service Registration
Version : 6.0 Sprint 6F.6A
=========================================================
"""

from __future__ import annotations

from typing import Optional

from Framework.service_container import (
    ServiceContainer,
)
from WalkForward.parameter_generator import (
    ParameterGenerator,
)
from WalkForward.parameter_space import (
    ParameterSpace,
)


def register_parameter_generator(
    services: ServiceContainer,
    *,
    parameter_space: ParameterSpace,
    random_seed: Optional[int] = None,
) -> ParameterGenerator:
    generator = ParameterGenerator(
        parameter_space=parameter_space,
        random_seed=random_seed,
    )

    services.register_instance(
        "optimization_parameter_space",
        parameter_space,
        replace=True,
    )

    services.register_instance(
        "optimization_parameter_generator",
        generator,
        replace=True,
    )

    return generator
