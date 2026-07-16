from __future__ import annotations

from pathlib import Path

from Research import (
    AIRankingEngine,
    Experiment,
    ExperimentMode,
    ExperimentRegistry,
    ExperimentRunner,
    LeaderboardExporter,
    ParameterSpace,
    ParetoEngine,
    ParetoReportExporter,
    PromotionEngine,
    ResearchResultStore,
    RunnerConfig,
    WalkForwardAdapter,
)
from Research.mock_walk_forward import (
    deterministic_mock_walk_forward,
)


PROJECT_ROOT = Path(__file__).resolve().parent


def main() -> None:
    print("=" * 94)
    print(" BursaAI v7 Sprint 7A.5 RC4 — Pareto + Confidence + Tier Gate")
    print("=" * 94)

    registry = ExperimentRegistry(
        PROJECT_ROOT / "Experiments"
    )

    result_store = ResearchResultStore(
        PROJECT_ROOT / "ResearchResults"
    )

    space = ParameterSpace(
        strategy_name="EMA_RSI_ATR",
        parameters={
            "ema_fast": [10, 20, 30],
            "ema_slow": [50, 100],
            "rsi_period": [8, 10, 14],
            "atr_multiplier": [1.5, 2.0],
        },
    )

    experiment = Experiment(
        name="Sprint 7A.5 RC4 Pareto Demo",
        description="Pareto, Confidence dan Tier Gate integration.",
        mode=ExperimentMode.PARALLEL,
        candidates=space.generate_grid_candidates(
            symbol="1155.KL",
            max_candidates=12,
        ),
        symbols=["1155.KL"],
    )

    registry.register(experiment)

    adapter = WalkForwardAdapter(
        deterministic_mock_walk_forward
    )

    runner = ExperimentRunner(
        registry=registry,
        evaluator=adapter.evaluator(
            experiment.experiment_id,
            result_callback=result_store.save,
        ),
        config=RunnerConfig(
            max_workers=4,
            checkpoint_every=2,
            max_retries=1,
        ),
    )

    runner.run(experiment)

    restored = registry.load(
        experiment.experiment_id
    )

    entries = result_store.list(
        experiment_id=restored.experiment_id
    )

    by_candidate = {
        item["candidate_id"]: item
        for item in entries
    }

    pairs = []

    for candidate in restored.candidates:
        entry = by_candidate.get(candidate.candidate_id)

        if entry is None:
            continue

        pairs.append(
            (
                candidate,
                result_store.load(entry["result_id"]),
            )
        )

    leaderboard = AIRankingEngine().rank(pairs)
    pareto_points = ParetoEngine().rank(leaderboard)
    promotions = PromotionEngine().evaluate(
        leaderboard,
        pareto_points,
    )

    ranking_outputs = LeaderboardExporter(
        PROJECT_ROOT / "Reports" / "Ranking"
    ).export_all(leaderboard)

    pareto_outputs = ParetoReportExporter(
        PROJECT_ROOT / "Reports" / "Pareto"
    ).export(
        pareto_points,
        promotions,
    )

    front_by_candidate = {
        point.candidate_id: point.front
        for point in pareto_points
    }

    decision_by_candidate = {
        item["candidate_id"]: item
        for item in promotions
    }

    print()
    print("PARETO AI LEADERBOARD")
    print("-" * 94)

    for item in leaderboard[:10]:
        decision = decision_by_candidate[
            item.candidate_id
        ]

        print(
            f"{item.rank:>2}. "
            f"{item.candidate_name:<24} "
            f"AI={item.breakdown.overall_score:>6.2f} "
            f"Conf={item.breakdown.confidence_score:>6.2f} "
            f"Pareto=F{front_by_candidate[item.candidate_id]} "
            f"Gate={decision['approved_tier']:<15} "
            f"Action={decision['action']}"
        )

    print()
    print("OUTPUT FILES")
    print("-" * 94)

    for name, path in {
        **ranking_outputs,
        **pareto_outputs,
    }.items():
        print(f"{name:<16}: {path}")

    print("=" * 94)
    print("SPRINT 7A.5 RC4 COMPLETED")
    print("=" * 94)


if __name__ == "__main__":
    main()
