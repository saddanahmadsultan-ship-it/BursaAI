"""
=========================================================
BursaAI Execution Adapter Registry
Version : 6.0 Sprint 5C.2
=========================================================
"""

from __future__ import annotations

from typing import Callable, Dict, Optional

from Adapters.confidence_adapter import ConfidenceAdapter
from Adapters.decision_adapter import DecisionAdapter
from Adapters.dynamic_risk_adapter import DynamicRiskAdapter
from Adapters.position_adapter import PositionAdapter
from Adapters.strategy_adapter import StrategyAdapter
from Framework.engine_registry import EngineRegistry
from Framework.event_bus import EventBus
from Framework.service_container import ServiceContainer


def register_execution_adapters(
    registry: EngineRegistry,
    *,
    confidence_function: Optional[Callable[..., Dict]] = None,
    strategy_function: Optional[Callable[..., Dict]] = None,
    decision_function: Optional[Callable[[Dict], Dict]] = None,
    risk_function: Optional[Callable[[Dict], Dict]] = None,
    position_function: Optional[Callable[[Dict], Dict]] = None,
    services: Optional[ServiceContainer] = None,
    event_bus: Optional[EventBus] = None,
    include_dynamic_risk: bool = True,
    include_position: bool = True,
) -> EngineRegistry:
    registry.register(
        ConfidenceAdapter(
            confidence_function=confidence_function,
            services=services,
            event_bus=event_bus,
        )
    )
    registry.register(
        StrategyAdapter(
            strategy_function=strategy_function,
            services=services,
            event_bus=event_bus,
        )
    )
    registry.register(
        DecisionAdapter(
            decision_function=decision_function,
            services=services,
            event_bus=event_bus,
        )
    )

    if include_dynamic_risk:
        registry.register(
            DynamicRiskAdapter(
                risk_function=risk_function,
                services=services,
                event_bus=event_bus,
            )
        )

    if include_position:
        registry.register(
            PositionAdapter(
                position_function=position_function,
                services=services,
                event_bus=event_bus,
            )
        )

    return registry
