from pathlib import Path

from MachineLearning import (
    FeaturePipelineConfig,
    ModelEvaluationReport,
    ModelTrainingSuite,
    ResearchFeaturePipeline,
)
from main_v7_dataset_builder import build_research_results

ROOT = Path(__file__).resolve().parent


def main() -> None:
    print("=" * 96)
    print(" BursaAI v7 Sprint 7B.3 — Model Training, Evaluation & Model Selection")
    print("=" * 96)

    ranked, pareto, promotions = build_research_results()
    dataset = ResearchFeaturePipeline(
        FeaturePipelineConfig(
            ROOT / "Datasets" / "Research",
            scale_features=True,
        )
    ).run(ranked, pareto, promotions)["dataset"]

    result = ModelTrainingSuite(
        ROOT / "Models" / "Sprint7B3"
    ).run(dataset)

    outputs = ModelEvaluationReport(
        ROOT / "Reports" / "ML"
    ).export(result["ranked_results"])

    print()
    print("MODEL LEADERBOARD")
    print("-" * 96)

    for index, item in enumerate(result["ranked_results"], start=1):
        print(
            f"{index:>2}. {item.model_name:<24} "
            f"Select={item.selection_score:>6.3f} "
            f"Val={item.validation_metrics.balanced_accuracy:>6.3f} "
            f"Test={item.test_metrics.balanced_accuracy:>6.3f} "
            f"F1={item.test_metrics.f1_score:>6.3f} "
            f"CV={item.cross_validation_mean:>6.3f} "
            f"Gap={item.generalization_gap:>6.3f}"
        )

    best = result["best_model"]
    print()
    print("BEST MODEL")
    print("-" * 96)
    print("Name            :", best.model_name)
    print("Selection Score :", best.selection_score)
    print("Test F1         :", best.test_metrics.f1_score)
    print("Stability       :", best.stability_score)
    print("Model Path      :", best.model_path)

    print()
    print("OUTPUT FILES")
    print("-" * 96)
    for name, path in outputs.items():
        print(f"{name:<10}: {path}")

    print("=" * 96)
    print("SPRINT 7B.3 COMPLETED")
    print("=" * 96)


if __name__ == "__main__":
    main()
