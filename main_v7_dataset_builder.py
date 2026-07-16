from __future__ import annotations

from pathlib import Path

from MachineLearning import (
    FeaturePipelineConfig,
    ResearchFeaturePipeline,
)
from Research import (
    AIRankingEngine,
    Experiment,
    ExperimentMode,
    ExperimentRegistry,
    ExperimentRunner,
    ParameterSpace,
    ParetoEngine,
    PromotionEngine,
    ResearchResultStore,
    RunnerConfig,
    WalkForwardAdapter,
)
from Research.mock_walk_forward import (
    deterministic_mock_walk_forward,
)


PROJECT_ROOT = Path(__file__).resolve().parent


def build_research_results():
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
        name="Sprint 7B.2 Dataset Builder Demo",
        description=(
            "Generate validated ML dataset from "
            "Research Engine outputs."
        ),
        mode=ExperimentMode.PARALLEL,
        candidates=space.generate_grid_candidates(
            symbol="1155.KL",
            max_candidates=20,
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
        entry = by_candidate.get(
            candidate.candidate_id
        )

        if entry is None:
            continue

        pairs.append(
            (
                candidate,
                result_store.load(
                    entry["result_id"]
                ),
            )
        )

    ranked = AIRankingEngine().rank(pairs)
    pareto = ParetoEngine().rank(ranked)
    promotions = PromotionEngine().evaluate(
        ranked,
        pareto,
    )

    return ranked, pareto, promotions


def main() -> None:
    print("=" * 92)
    print(
        " BursaAI v7 Sprint 7B.2 — "
        "Research Dataset Builder + Feature Engineering"
    )
    print("=" * 92)

    ranked, pareto, promotions = (
        build_research_results()
    )

    pipeline = ResearchFeaturePipeline(
        FeaturePipelineConfig(
            output_dir=(
                PROJECT_ROOT
                / "Datasets"
                / "Research"
            ),
            scale_features=False,
            fail_on_validation_error=True,
        )
    )

    result = pipeline.run(
        ranked,
        pareto,
        promotions,
    )

    dataset = result["dataset"]
    validation = result["validation"]

    print()
    print("DATASET RESULT")
    print("-" * 92)
    print("Samples          :", dataset.size)
    print(
        "Features         :",
        len(dataset.feature_names),
    )
    print(
        "Positive labels  :",
        validation.positive_count,
    )
    print(
        "Negative labels  :",
        validation.negative_count,
    )
    print(
        "Duplicate rows   :",
        validation.duplicate_count,
    )
    print(
        "Validation       :",
        "PASSED" if validation.passed else "FAILED",
    )

    print()
    print("OUTPUT FILES")
    print("-" * 92)

    for name, path in result["outputs"].items():
        print(f"{name:<10}: {path}")

    print("=" * 92)
    print("SPRINT 7B.2 COMPLETED")
    print("=" * 92)


if __name__ == "__main__":
    main()
