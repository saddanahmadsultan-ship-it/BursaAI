"""
=========================================================
BursaAI Analysis Adapter Registration
Version : 6.0 Sprint 4C
=========================================================
"""

from __future__ import annotations

from typing import Callable, Dict, Optional

from Adapters.momentum_adapter import MomentumAdapter
from Adapters.score_adapter import ScoreAdapter
from Adapters.trend_adapter import TrendAdapter
from Framework.engine_registry import EngineRegistry


def register_analysis_adapters(
    registry: EngineRegistry,
    *,
    scorer: Optional[Callable[[object], Dict]] = None,
    trend_function: Optional[Callable[[object], Dict]] = None,
    momentum_function: Optional[Callable[[object], Dict]] = None,
    include_score: bool = True,
    include_trend: bool = True,
    include_momentum: bool = True,
) -> EngineRegistry:
    """
    Register Sprint 4C analysis adapters.
    """

    if include_score:
        registry.register(
            ScoreAdapter(
                scorer=scorer,
            )
        )

    if include_trend:
        registry.register(
            TrendAdapter(
                trend_function=trend_function,
            )
        )

    if include_momentum:
        registry.register(
            MomentumAdapter(
                momentum_function=momentum_function,
            )
        )

    return registry
