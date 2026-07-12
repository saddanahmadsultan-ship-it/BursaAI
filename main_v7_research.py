from __future__ import annotations

from pathlib import Path

from Research import (
    Experiment,
    ExperimentMode,
    ExperimentRegistry,
    ExperimentRunner,
    ParameterSpace,
    ResearchResultStore,
    RunnerConfig,
    WalkForwardAdapter,
    WalkForwardAdapterConfig,
)
from Research.mock_walk_forward import (
    deterministic_mock_walk_forward,
)


PROJECT_ROOT = Path(__file__).resolve().parent


def main() -> None:
    print("=" * 72)
    print("           BursaAI v7 Research Platform — Sprint 7A.4")
    print("=" * 72)

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
        name="Sprint 7A.4 Walk Forward Research Demo",
        description=(
            "Walk Forward Adapter dan Result Store integration."
        ),
        mode=ExperimentMode.PARALLEL,
        candidates=space.generate_grid_candidates(
            symbol="1155.KL",
            max_candidates=12,
        ),
        symbols=["1155.KL"],
    )

    registry.register(experiment)

    adapter = WalkForwardAdapter(
        deterministic_mock_walk_forward,
        WalkForwardAdapterConfig(
            minimum_folds=3,
            require_equity_curve=True,
        ),
    )

    evaluator = adapter.evaluator(
        experiment.experiment_id,
        result_callback=result_store.save,
    )

    runner = ExperimentRunner(
        registry=registry,
        evaluator=evaluator,
        config=RunnerConfig(
            max_workers=4,
            checkpoint_every=2,
            max_retries=1,
        ),
    )

    stats = runner.run(experiment)

    restored = registry.load(
        experiment.experiment_id
    )

    best_candidate = restored.best_candidate()
    best_result = result_store.best_result(
        experiment.experiment_id
    )

    print()
    print("Experiment ID :", restored.experiment_id)
    print("Status        :", restored.status.value)
    print("Candidates    :", restored.total_candidates)
    print("Completed     :", restored.completed_candidates)
    print("Failed        :", restored.failed_candidates)
    print("Progress      :", f"{restored.progress_percentage():.2f}%")
    print("Runner Stats  :", stats.to_dict())
    print("Stored Results:", len(result_store.list(
        experiment_id=restored.experiment_id
    )))

    if best_candidate is not None:
        print()
        print("BEST CANDIDATE")
        print("-" * 72)
        print("Name          :", best_candidate.name)
        print("Parameters    :", best_candidate.parameters)
        print(
            "Final Score   :",
            f"{best_candidate.metrics.final_score:.2f}",
        )
        print(
            "CAGR          :",
            f"{best_candidate.metrics.cagr:.2f}%",
        )
        print(
            "Sharpe        :",
            f"{best_candidate.metrics.sharpe_ratio:.2f}",
        )
        print(
            "Max Drawdown  :",
            f"{best_candidate.metrics.max_drawdown:.2f}%",
        )

    if best_result is not None:
        print(
            "WalkForward   :",
            f"{len(best_result.walk_forward_folds)} folds",
        )
        print(
            "Equity Points :",
            len(best_result.equity_curve),
        )

    print()
    print("=" * 72)
    print("SPRINT 7A.4 RELEASE PACK VALIDATION COMPLETED")
    print("=" * 72)


if __name__ == "__main__":
    main()
