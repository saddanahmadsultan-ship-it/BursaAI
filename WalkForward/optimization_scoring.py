"""
=========================================================
BursaAI Optimization Scoring
Version : 6.0 Sprint 6F.6B
=========================================================
"""

from __future__ import annotations

from typing import Dict, Mapping


DEFAULT_WEIGHTS = {
    "robustness_score": 0.35,
    "profit_factor": 0.25,
    "sharpe_ratio": 0.15,
    "drawdown_score": 0.10,
    "win_rate": 0.10,
    "stability_score": 0.05,
}


def normalize_metric(
    name: str,
    value: float,
) -> float:
    value = float(value)

    if name in {
        "robustness_score",
        "stability_score",
        "win_rate",
        "drawdown_score",
    }:
        return max(
            min(value, 100.0),
            0.0,
        )

    if name == "profit_factor":
        return max(
            min(value / 3.0 * 100.0, 100.0),
            0.0,
        )

    if name == "sharpe_ratio":
        return max(
            min(value / 3.0 * 100.0, 100.0),
            0.0,
        )

    return max(
        min(value, 100.0),
        0.0,
    )


def calculate_optimization_score(
    metrics: Mapping[str, float],
    *,
    weights: Mapping[str, float] | None = None,
) -> float:
    selected_weights = dict(
        weights or DEFAULT_WEIGHTS
    )

    total_weight = sum(
        float(value)
        for value in selected_weights.values()
    )

    if total_weight <= 0:
        return 0.0

    score = 0.0

    for name, weight in selected_weights.items():
        normalized = normalize_metric(
            name,
            float(
                metrics.get(name, 0.0)
            ),
        )

        score += normalized * float(weight)

    return round(
        score / total_weight,
        4,
    )
