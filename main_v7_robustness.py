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
    ResearchResultStore,
    RunnerConfig,
    WalkForwardAdapter,
)
from Research.mock_walk_forward import (
    deterministic_mock_walk_forward,
)


PROJECT_ROOT = Path(__file__).resolve().parent


def main() -> None:
    print("=" * 82)
    print("      BursaAI v7 Sprint 7A.5 RC2 — Robustness Engine")
    print("=" * 82)

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
        name="Sprint 7A.5 RC2 Robustness Demo",
        description="Robustness Engine integration.",
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

    pairs = []

    result_entries = result_store.list(
        experiment_id=restored.experiment_id
    )

    by_candidate = {
        item["candidate_id"]: item
        for item in result_entries
    }

    for candidate in restored.candidates:
        entry = by_candidate.get(
            candidate.candidate_id
        )

        if entry is None:
            continue

        result = result_store.load(
            entry["result_id"]
        )

        pairs.append((candidate, result))

    leaderboard = AIRankingEngine().rank(pairs)

    outputs = LeaderboardExporter(
        PROJECT_ROOT / "Reports" / "Ranking"
    ).export_all(leaderboard)

    print()
    print("ROBUSTNESS LEADERBOARD")
    print("-" * 82)

    for item in leaderboard[:10]:
        robust = item.robustness_breakdown

        print(
            f"{item.rank:>2}. "
            f"{item.candidate_name:<24} "
            f"AI={item.breakdown.overall_score:>6.2f} "
            f"Robust={item.breakdown.robustness_score:>6.2f} "
            f"Fold={robust.fold_success_score:>6.2f} "
            f"Degrade={robust.degradation_score:>6.2f} "
            f"Tier={item.tier}"
        )

    print()
    print("OUTPUT FILES")
    print("-" * 82)

    for name, path in outputs.items():
        print(f"{name:<10}: {path}")

    print("=" * 82)
    print("SPRINT 7A.5 RC2 COMPLETED")
    print("=" * 82)


if __name__ == "__main__":
    main()
