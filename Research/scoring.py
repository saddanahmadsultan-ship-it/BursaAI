from __future__ import annotations

from typing import Iterable, List


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, float(value)))


def normalize_positive(value: float, target: float) -> float:
    if target <= 0:
        return 0.0
    return clamp(float(value) / float(target) * 100.0)


def normalize_inverse(value: float, maximum_acceptable: float) -> float:
    if maximum_acceptable <= 0:
        return 0.0
    return clamp((1.0 - float(value) / float(maximum_acceptable)) * 100.0)


def mean(values: Iterable[float]) -> float:
    items: List[float] = [float(value) for value in values]
    if not items:
        return 0.0
    return sum(items) / len(items)
