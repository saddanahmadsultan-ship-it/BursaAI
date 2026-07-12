"""
=========================================================
BursaAI Optimization Summary
Version : 6.0 Sprint 6F.6C
=========================================================
"""

from __future__ import annotations

from typing import Any, Dict

from WalkForward.optimization_models import (
    OptimizationRunResult,
)


def build_optimization_summary(
    result: OptimizationRunResult,
) -> Dict[str, Any]:
    scores = [
        candidate.optimization_score
        for candidate in result.candidates
        if candidate.success
    ]

    average_score = (
        sum(scores) / len(scores)
        if scores
        else 0.0
    )

    best = result.best_candidate

    return {
        "strategy_name": result.strategy_name,
        "total_candidates": result.total_candidates,
        "completed_candidates": result.completed_candidates,
        "failed_candidates": result.failed_candidates,
        "success_rate_percent": round(
            (
                result.completed_candidates
                / result.total_candidates
                * 100
            )
            if result.total_candidates > 0
            else 0.0,
            4,
        ),
        "average_score": round(
            average_score,
            4,
        ),
        "best_candidate_id": (
            best.parameter_id
            if best is not None
            else None
        ),
        "best_score": (
            best.optimization_score
            if best is not None
            else 0.0
        ),
        "best_parameters": (
            dict(best.parameters)
            if best is not None
            else {}
        ),
        "duration_ms": round(
            result.duration_ms,
            4,
        ),
    }
