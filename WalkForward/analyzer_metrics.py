"""
=========================================================
BursaAI Walk Forward Analyzer Metrics
Version : 6.0 Sprint 6F.5
=========================================================
"""

from __future__ import annotations

from statistics import mean, pstdev
from typing import Iterable, List


def safe_mean(values: Iterable[float]) -> float:
    values = list(values)
    return mean(values) if values else 0.0


def degradation_percent(
    training_value: float,
    validation_value: float,
) -> float:
    training_value = float(training_value)
    validation_value = float(validation_value)

    if training_value == 0:
        return 0.0

    return (
        (training_value - validation_value)
        / abs(training_value)
        * 100
    )


def stability_score(
    values: List[float],
) -> float:
    if not values:
        return 0.0

    if len(values) == 1:
        return 100.0

    average = safe_mean(values)

    if average == 0:
        return 0.0

    deviation = pstdev(values)
    coefficient = abs(
        deviation / average
    )

    score = 100.0 - min(
        coefficient * 100.0,
        100.0,
    )

    return max(score, 0.0)


def consistency_score(
    passed_windows: int,
    total_windows: int,
) -> float:
    if total_windows <= 0:
        return 0.0

    return (
        passed_windows
        / total_windows
        * 100.0
    )


def robustness_score(
    stability: float,
    consistency: float,
    average_degradation: float,
) -> float:
    degradation_component = max(
        0.0,
        100.0 - max(
            average_degradation,
            0.0,
        ),
    )

    score = (
        stability * 0.35
        + consistency * 0.40
        + degradation_component * 0.25
    )

    return max(
        min(score, 100.0),
        0.0,
    )
