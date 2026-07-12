"""
=========================================================
BursaAI Parameter Templates
Version : 6.0 Sprint 6F.6A
=========================================================
"""

from __future__ import annotations

from WalkForward.parameter_space import (
    ParameterSpace,
)


def build_default_trading_parameter_space(
) -> ParameterSpace:
    space = ParameterSpace()

    space.add(
        "ema_fast",
        [5, 8, 10, 13, 20, 21, 34],
        validator=lambda value: int(value) > 0,
    )

    space.add(
        "ema_slow",
        [30, 50, 55, 89, 100, 150],
        validator=lambda value: int(value) > 0,
    )

    space.add(
        "rsi_period",
        [7, 9, 14, 21],
        validator=lambda value: int(value) > 0,
    )

    space.add(
        "atr_period",
        [7, 10, 14, 20],
        validator=lambda value: int(value) > 0,
    )

    space.add_constraint(
        lambda parameters: (
            parameters["ema_fast"]
            < parameters["ema_slow"]
        )
    )

    return space
