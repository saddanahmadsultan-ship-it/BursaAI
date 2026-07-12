"""
=========================================================
BursaAI Analytics Statistics
Version : 6.0 Sprint 6E
=========================================================
"""

from __future__ import annotations

from math import sqrt
from statistics import mean, pstdev
from typing import Iterable, List


def safe_mean(values: Iterable[float]) -> float:
    values = list(values)
    return mean(values) if values else 0.0


def safe_std(values: Iterable[float]) -> float:
    values = list(values)
    return pstdev(values) if len(values) > 1 else 0.0


def sharpe_ratio(
    returns: List[float],
    annualization_factor: float = 252.0,
) -> float:
    if not returns:
        return 0.0

    average = safe_mean(returns)
    deviation = safe_std(returns)

    if deviation <= 0:
        return 0.0

    return (
        average
        / deviation
        * sqrt(annualization_factor)
    )


def sortino_ratio(
    returns: List[float],
    annualization_factor: float = 252.0,
) -> float:
    if not returns:
        return 0.0

    downside = [
        value
        for value in returns
        if value < 0
    ]

    downside_deviation = safe_std(downside)

    if downside_deviation <= 0:
        return 0.0

    return (
        safe_mean(returns)
        / downside_deviation
        * sqrt(annualization_factor)
    )
