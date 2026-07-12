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
    print("=" * 76)
    print("         BursaAI v7 Sprint 7A.5 RC1 — AI Ranking Core")
    print("=" * 76)

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
        name="Sprint 7A.5 RC1 Ranking Demo",
        description="AI Ranking Core integration demo.",
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

    for candidate in restored.candidates:
        result_entries = [
            item
            for item in result_store.list(
                experiment_id=restored.experiment_id
            )
            if item["candidate_id"] == candidate.candidate_id
        ]

        if not result_entries:
            continue

        result = result_store.load(
            result_entries[0]["result_id"]
        )

        pairs.append((candidate, result))

    ranking_engine = AIRankingEngine()
    leaderboard = ranking_engine.rank(pairs)

    exporter = LeaderboardExporter(
        PROJECT_ROOT / "Reports" / "Ranking"
    )

    output_files = exporter.export_all(leaderboard)

    print()
    print("TOP AI STRATEGIES")
    print("-" * 76)

    for item in leaderboard[:10]:
        print(
            f"{item.rank:>2}. "
            f"{item.candidate_name:<24} "
            f"AI={item.breakdown.overall_score:>6.2f} "
            f"Perf={item.breakdown.performance_score:>6.2f} "
            f"Risk={item.breakdown.risk_score:>6.2f} "
            f"Tier={item.tier}"
        )

    print()
    print("OUTPUT FILES")
    print("-" * 76)

    for name, path in output_files.items():
        print(f"{name:<10}: {path}")

    print("=" * 76)
    print("SPRINT 7A.5 RC1 COMPLETED")
    print("=" * 76)


if __name__ == "__main__":
    main()
