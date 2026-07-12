"""
=========================================================
BursaAI Portfolio Service Registration
Version : 6.0 Sprint 5C.3
=========================================================
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional

from Adapters.portfolio_allocator_adapter import (
    PortfolioAllocatorAdapter,
)
from Framework.event_bus import EventBus
from Framework.service_container import ServiceContainer


def register_portfolio_allocator(
    services: ServiceContainer,
    *,
    allocator_function: Optional[Callable[[List[Dict]], Dict]] = None,
    event_bus: Optional[EventBus] = None,
    replace: bool = True,
) -> PortfolioAllocatorAdapter:
    adapter = PortfolioAllocatorAdapter(
        allocator_function=allocator_function,
        services=services,
        event_bus=event_bus,
    )

    services.register_instance(
        "portfolio_allocator_adapter",
        adapter,
        replace=replace,
    )

    return adapter
