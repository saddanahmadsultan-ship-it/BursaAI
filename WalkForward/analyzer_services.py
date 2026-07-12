"""
=========================================================
BursaAI Walk Forward Analyzer Service Registration
Version : 6.0 Sprint 6F.5
=========================================================
"""

from __future__ import annotations

from Framework.service_container import (
    ServiceContainer,
)
from WalkForward.walkforward_analyzer import (
    WalkForwardAnalyzer,
)


def register_walkforward_analyzer(
    services: ServiceContainer,
    *,
    maximum_degradation_percent: float = 30.0,
    minimum_validation_metric: float = 0.0,
    minimum_pass_rate_percent: float = 60.0,
) -> WalkForwardAnalyzer:
    analyzer = WalkForwardAnalyzer(
        maximum_degradation_percent=(
            maximum_degradation_percent
        ),
        minimum_validation_metric=(
            minimum_validation_metric
        ),
        minimum_pass_rate_percent=(
            minimum_pass_rate_percent
        ),
        services=services,
    )

    services.register_instance(
        "walkforward_analyzer",
        analyzer,
        replace=True,
    )

    return analyzer
