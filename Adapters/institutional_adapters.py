"""
=========================================================
BursaAI Institutional Adapter Registration
Version : 6.0 Sprint 4D
=========================================================
"""

from __future__ import annotations

from typing import Callable, Dict, Optional

from Adapters.quality_gate_adapter import QualityGateAdapter
from Adapters.smart_money_adapter import SmartMoneyAdapter
from Adapters.volume_adapter import VolumeAdapter
from Framework.engine_registry import EngineRegistry


def register_institutional_adapters(
    registry: EngineRegistry,
    *,
    volume_function: Optional[Callable[[object], Dict]] = None,
    quality_function: Optional[Callable[[Dict], Dict]] = None,
    smart_money_function: Optional[
        Callable[[object, Dict], Dict]
    ] = None,
    include_volume: bool = True,
    include_quality: bool = True,
    include_smart_money: bool = True,
) -> EngineRegistry:
    """
    Register Volume, Quality Gate and Smart Money adapters.
    """

    if include_volume:
        registry.register(
            VolumeAdapter(
                volume_function=volume_function,
            )
        )

    if include_quality:
        registry.register(
            QualityGateAdapter(
                quality_function=quality_function,
            )
        )

    if include_smart_money:
        registry.register(
            SmartMoneyAdapter(
                smart_money_function=smart_money_function,
            )
        )

    return registry
