"""
BursaAI v6.0 Sprint 6F.6C Full Optimization Integration Test.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Framework.infrastructure import (
    build_infrastructure,
)
from WalkForward.optimization_report import (
    OptimizationReport,
)
from WalkForward.optimization_services import (
    register_optimization_engine,
)
from WalkForward.optimization_workflow_services import (
    register_optimization_workflow,
)
from WalkForward.parameter_services import (
    register_parameter_generator,
)
from WalkForward.parameter_space import (
    ParameterSpace,
)


def fake_evaluator(parameters, context=None):
    if hasattr(parameters, "parameters"):
        parameters = parameters.parameters

    fast = parameters["ema_fast"]
    slow = parameters["ema_slow"]
    rsi = parameters["rsi_period"]

    distance_fast = abs(
        fast - 10
    )
    distance_slow = abs(
        slow - 50
    )
    distance_rsi = abs(
        rsi - 14
    )

    robustness = (
        96
        - distance_fast * 2
        - distance_slow * 0.4
        - distance_rsi * 0.8
    )

    profit_factor = (
        2.3
        - distance_fast * 0.03
        - distance_slow * 0.01
        - distance_rsi * 0.02
    )

    sharpe = (
        1.9
        - distance_fast * 0.04
        - distance_slow * 0.01
    )

    drawdown_score = (
        90
        - distance_fast
        - distance_slow * 0.15
    )

    win_rate = (
        64
        - distance_fast * 0.5
        - distance_rsi * 0.3
    )

    stability = (
        92
        - distance_slow * 0.25
        - distance_rsi * 0.4
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
            "strategy_code": (
                f"EMA_{fast}_{slow}_RSI_{rsi}"
            ),
        },
        "warnings": [],
    }


def build_space():
    space = ParameterSpace()

    space.add(
        "ema_fast",
        [5, 10, 15],
    )

    space.add(
        "ema_slow",
        [30, 50, 70],
    )

    space.add(
        "rsi_period",
        [7, 14],
    )

    space.add_constraint(
        lambda parameters: (
            parameters["ema_fast"]
            < parameters["ema_slow"]
        )
    )

    return space


def main():
    infrastructure = build_infrastructure()
    events = []

    infrastructure.events.subscribe(
        "OptimizationWorkflowCompleted",
        lambda event: events.append(event),
    )

    space = build_space()

    register_parameter_generator(
        infrastructure.services,
        parameter_space=space,
        random_seed=42,
    )

    register_optimization_engine(
        infrastructure.services,
        evaluator=fake_evaluator,
        optimizer_name="grid",
    )

    workflow = register_optimization_workflow(
        infrastructure.services
    )

    result = workflow.run_grid(
        strategy_name="ema_rsi",
        top_n=3,
    )

    run = result.run_result

    assert run.success is True
    assert run.total_candidates == 18
    assert run.completed_candidates == 18
    assert run.failed_candidates == 0
    assert run.best_candidate is not None

    assert run.best_candidate.parameters == {
        "ema_fast": 10,
        "ema_slow": 50,
        "rsi_period": 14,
    }

    assert (
        result.summary["best_candidate_id"]
        == run.best_candidate.parameter_id
    )

    assert (
        result.summary["best_parameters"]
        == run.best_candidate.parameters
    )

    assert (
        result.summary["success_rate_percent"]
        == 100.0
    )

    assert (
        "BURSAAI OPTIMIZATION REPORT"
        in result.report_text
    )

    assert (
        "TOP CANDIDATES"
        in result.report_text
    )

    assert (
        "Best Parameters"
        in result.report_text
    )

    report = OptimizationReport(
        result=run,
        top_n=3,
    )

    ranked = report.ranked_candidates()

    assert len(ranked) == 18
    assert (
        ranked[0].optimization_score
        >= ranked[1].optimization_score
    )
    assert (
        ranked[0].parameters
        == run.best_candidate.parameters
    )

    assert len(
        report.top_candidates()
    ) == 3

    assert len(events) == 1
    assert (
        events[0].payload["summary"][
            "best_parameters"
        ]
        == {
            "ema_fast": 10,
            "ema_slow": 50,
            "rsi_period": 14,
        }
    )

    assert (
        infrastructure.services.resolve(
            "optimization_workflow"
        )
        is workflow
    )

    random_result = workflow.run_random(
        5,
        strategy_name="ema_rsi_random",
        top_n=2,
    )

    assert (
        random_result.run_result.total_candidates
        == 5
    )

    assert (
        random_result.run_result.completed_candidates
        == 5
    )

    print("=" * 96)
    print("BURSAAI v6.0 SPRINT 6F.6C TEST")
    print("=" * 96)
    print("Parameter Generator Integration : OK")
    print("Optimization Engine Integration : OK")
    print("Optimization Registry           : OK")
    print("Grid Workflow                   : OK")
    print("Random Workflow                 : OK")
    print("Candidate Ranking               : OK")
    print("Best Candidate Summary          : OK")
    print("Top Candidate Report            : OK")
    print("Workflow Event                  : OK")
    print("Service Registration            : OK")
    print("Full End-to-End Integration     : OK")
    print("=" * 96)
    print("SPRINT 6F.6C OPTIMIZATION REPORT & FULL INTEGRATION OK")


if __name__ == "__main__":
    main()
