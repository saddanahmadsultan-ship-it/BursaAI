"""
BursaAI v6.0 Sprint 6F.6B Optimization Engine test.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Framework.infrastructure import build_infrastructure
from WalkForward.optimization_services import (
    register_optimization_engine,
)
from WalkForward.parameter_generator import ParameterGenerator
from WalkForward.parameter_space import ParameterSpace


def build_parameter_sets():
    space = ParameterSpace()

    space.add(
        "ema_fast",
        [5, 10, 20],
    )

    space.add(
        "ema_slow",
        [30, 50],
    )

    space.add_constraint(
        lambda parameters: (
            parameters["ema_fast"]
            < parameters["ema_slow"]
        )
    )

    return ParameterGenerator(
        parameter_space=space,
        random_seed=7,
    ).generate_grid()


def fake_evaluator(parameters, context=None):
    if hasattr(parameters, "parameters"):
        parameters = parameters.parameters

    fast = parameters["ema_fast"]
    slow = parameters["ema_slow"]

    robustness = (
        95
        - abs(fast - 10) * 2
        - abs(slow - 50) * 0.5
    )

    profit_factor = (
        1.5
        + (10 / fast) * 0.2
        + (50 / slow) * 0.3
    )

    sharpe = (
        1.0
        + (10 / fast) * 0.25
    )

    win_rate = (
        50
        + (20 - abs(fast - 10)) * 0.5
    )

    stability = (
        90
        - abs(slow - 50) * 0.4
    )

    drawdown_score = (
        85
        - abs(fast - 10)
    )

    return {
        "metrics": {
            "robustness_score": robustness,
            "profit_factor": profit_factor,
            "sharpe_ratio": sharpe,
            "drawdown_score": drawdown_score,
            "win_rate": win_rate,
            "stability_score": stability,
        },
        "artifacts": {
            "model": (
                f"EMA_{fast}_{slow}"
            ),
        },
        "warnings": [],
    }


def main():
    infrastructure = build_infrastructure()
    events = []

    infrastructure.events.subscribe(
        "OptimizationCandidateCompleted",
        lambda event: events.append(event.name),
    )

    infrastructure.events.subscribe(
        "OptimizationRunCompleted",
        lambda event: events.append(event.name),
    )

    engine = register_optimization_engine(
        infrastructure.services,
        evaluator=fake_evaluator,
        optimizer_name="grid",
    )

    parameter_sets = build_parameter_sets()

    result = engine.run(
        parameter_sets,
        strategy_name="ema_cross",
    )

    assert result.success is True
    assert result.total_candidates == 6
    assert result.completed_candidates == 6
    assert result.failed_candidates == 0
    assert result.best_candidate is not None
    assert result.best_candidate.parameters == {
        "ema_fast": 10,
        "ema_slow": 50,
    }
    assert (
        result.best_candidate.optimization_score
        > 70
    )
    assert (
        result.best_candidate.artifacts["model"]
        == "EMA_10_50"
    )

    assert events.count(
        "OptimizationCandidateCompleted"
    ) == 6

    assert events.count(
        "OptimizationRunCompleted"
    ) == 1

    registry = infrastructure.services.resolve(
        "optimization_registry"
    )

    assert registry.names() == [
        "grid"
    ]

    assert (
        registry.get("grid")
        is engine
    )

    assert (
        infrastructure.services.resolve(
            "optimization_engine"
        )
        is engine
    )

    candidate_ids = [
        candidate.parameter_id
        for candidate in result.candidates
    ]

    assert candidate_ids == [
        1,
        2,
        3,
        4,
        5,
        6,
    ]

    print("=" * 94)
    print("BURSAAI v6.0 SPRINT 6F.6B TEST")
    print("=" * 94)
    print("Optimization Candidate Model : OK")
    print("Optimization Run Model       : OK")
    print("Optimization Scoring         : OK")
    print("Single Candidate Evaluation  : OK")
    print("Multiple Candidate Run       : OK")
    print("Best Candidate Selection     : OK")
    print("Artifact Capture             : OK")
    print("Optimization Registry        : OK")
    print("Candidate Event              : OK")
    print("Run Event                    : OK")
    print("Service Registration         : OK")
    print("=" * 94)
    print("SPRINT 6F.6B OPTIMIZATION ENGINE & REGISTRY OK")


if __name__ == "__main__":
    main()
