"""
=========================================================
BursaAI Full Pipeline Registry
Version : 6.0 Sprint 5C.2
=========================================================
"""

from __future__ import annotations

from typing import Iterable, Optional

from Adapters.ai_layer_adapters import register_ai_layer_adapters
from Adapters.analysis_adapters import register_analysis_adapters
from Adapters.data_adapters import register_data_adapters
from Adapters.execution_adapters import register_execution_adapters
from Adapters.institutional_adapters import register_institutional_adapters
from Framework.engine_registry import EngineRegistry
from Framework.event_bus import EventBus
from Framework.service_container import ServiceContainer


def register_full_analysis_pipeline(
    registry: EngineRegistry,
    *,
    data_loader=None,
    indicator_function=None,
    scorer=None,
    trend_function=None,
    momentum_function=None,
    volume_function=None,
    quality_function=None,
    smart_money_function=None,
    regime_function=None,
    timing_function=None,
    brain_function=None,
    confidence_function=None,
    strategy_function=None,
    decision_function=None,
    risk_function=None,
    position_function=None,
    services: Optional[ServiceContainer] = None,
    event_bus: Optional[EventBus] = None,
    minimum_rows: int = 1,
    required_indicator_columns: Optional[Iterable[str]] = None,
    include_execution_layer: bool = True,
    include_dynamic_risk: bool = True,
    include_position: bool = True,
) -> EngineRegistry:
    register_data_adapters(
        registry,
        data_loader=data_loader,
        indicator_function=indicator_function,
        minimum_rows=minimum_rows,
        required_indicator_columns=required_indicator_columns,
    )

    register_analysis_adapters(
        registry,
        scorer=scorer,
        trend_function=trend_function,
        momentum_function=momentum_function,
    )

    register_institutional_adapters(
        registry,
        volume_function=volume_function,
        quality_function=quality_function,
        smart_money_function=smart_money_function,
    )

    register_ai_layer_adapters(
        registry,
        regime_function=regime_function,
        timing_function=timing_function,
        brain_function=brain_function,
        services=services,
        event_bus=event_bus,
    )

    if include_execution_layer:
        register_execution_adapters(
            registry,
            confidence_function=confidence_function,
            strategy_function=strategy_function,
            decision_function=decision_function,
            risk_function=risk_function,
            position_function=position_function,
            services=services,
            event_bus=event_bus,
            include_dynamic_risk=include_dynamic_risk,
            include_position=include_position,
        )

    return registry
