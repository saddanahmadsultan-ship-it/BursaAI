"""
=========================================================
BursaAI AI Layer Adapter Registration
Version : 6.0 Sprint 5A.3
=========================================================
"""

from __future__ import annotations

from typing import Callable, Dict, Optional

from Adapters.ai_brain_adapter import AIBrainAdapter
from Adapters.entry_timing_adapter import (
    EntryTimingAdapter,
)
from Adapters.market_regime_adapter import (
    MarketRegimeAdapter,
)
from Framework.engine_registry import EngineRegistry
from Framework.event_bus import EventBus
from Framework.service_container import ServiceContainer


def register_market_regime_adapter(
    registry: EngineRegistry,
    *,
    regime_function: Optional[
        Callable[[object, Dict], Dict]
    ] = None,
    services: Optional[ServiceContainer] = None,
    event_bus: Optional[EventBus] = None,
) -> EngineRegistry:
    registry.register(
        MarketRegimeAdapter(
            regime_function=regime_function,
            services=services,
            event_bus=event_bus,
        )
    )

    return registry


def register_entry_timing_adapter(
    registry: EngineRegistry,
    *,
    timing_function: Optional[
        Callable[[object, Dict], Dict]
    ] = None,
    services: Optional[ServiceContainer] = None,
    event_bus: Optional[EventBus] = None,
) -> EngineRegistry:
    registry.register(
        EntryTimingAdapter(
            timing_function=timing_function,
            services=services,
            event_bus=event_bus,
        )
    )

    return registry


def register_ai_brain_adapter(
    registry: EngineRegistry,
    *,
    brain_function: Optional[
        Callable[[Dict], Dict]
    ] = None,
    services: Optional[ServiceContainer] = None,
    event_bus: Optional[EventBus] = None,
) -> EngineRegistry:
    registry.register(
        AIBrainAdapter(
            brain_function=brain_function,
            services=services,
            event_bus=event_bus,
        )
    )

    return registry


def register_ai_layer_adapters(
    registry: EngineRegistry,
    *,
    regime_function: Optional[
        Callable[[object, Dict], Dict]
    ] = None,
    timing_function: Optional[
        Callable[[object, Dict], Dict]
    ] = None,
    brain_function: Optional[
        Callable[[Dict], Dict]
    ] = None,
    services: Optional[ServiceContainer] = None,
    event_bus: Optional[EventBus] = None,
    include_market_regime: bool = True,
    include_entry_timing: bool = True,
    include_ai_brain: bool = True,
) -> EngineRegistry:
    if include_market_regime:
        register_market_regime_adapter(
            registry,
            regime_function=regime_function,
            services=services,
            event_bus=event_bus,
        )

    if include_entry_timing:
        register_entry_timing_adapter(
            registry,
            timing_function=timing_function,
            services=services,
            event_bus=event_bus,
        )

    if include_ai_brain:
        register_ai_brain_adapter(
            registry,
            brain_function=brain_function,
            services=services,
            event_bus=event_bus,
        )

    return registry
