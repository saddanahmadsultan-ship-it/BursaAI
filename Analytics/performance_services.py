"""
=========================================================
BursaAI Performance Service Registration
Version : 6.0 Sprint 6E
=========================================================
"""

from __future__ import annotations

from Analytics.performance_engine import (
    PerformanceEngine,
)
from Framework.service_container import (
    ServiceContainer,
)


def register_performance_analytics(
    services: ServiceContainer,
    *,
    starting_capital: float = 100000.0,
) -> PerformanceEngine:
    journal = services.resolve(
        "trade_journal"
    )

    engine = PerformanceEngine(
        journal=journal,
        starting_capital=starting_capital,
    )

    services.register_instance(
        "performance_engine",
        engine,
        replace=True,
    )

    return engine
