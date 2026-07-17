from pathlib import Path

from MachineLearning import (
    ActiveModelRegistry,
    FeaturePipelineConfig,
    MLPredictionService,
    ModelTrainingSuite,
    PredictionReport,
    ResearchFeaturePipeline,
    ResearchMLPromotionIntegrator,
)
from main_v7_dataset_builder import build_research_results


ROOT = Path(__file__).resolve().parent


def _as_dict(item):
    return item.to_dict() if hasattr(item, "to_dict") else dict(item)


def main():
    print("=" * 100)
    print(
        " BursaAI v7 Sprint 7B.4 — "
        "ML Prediction Service + Research Promotion Integration"
    )
    print("=" * 100)

    ranked, pareto, promotions = build_research_results()

    feature = ResearchFeaturePipeline(
        FeaturePipelineConfig(
            ROOT / "Datasets" / "Research",
            scale_features=False,
            fail_on_validation_error=True,
        )
    ).run(ranked, pareto, promotions)

    trained = ModelTrainingSuite(
        ROOT / "Models" / "Sprint7B4"
    ).run(feature["dataset"])

    best = trained["best_model"]

    ActiveModelRegistry(
        ROOT / "Models" / "Sprint7B4"
    ).promote_champion(
        best.model_path,
        best.model_name,
        best.selection_score,
        feature["dataset"].feature_names,
    )

    service = MLPredictionService(
        ROOT / "Models" / "Sprint7B4"
    )
    integrator = ResearchMLPromotionIntegrator(service)

    pareto_map = {
        _as_dict(item)["candidate_id"]: _as_dict(item)
        for item in pareto
    }
    promo_map = {
        item["candidate_id"]: item
        for item in promotions
    }

    predictions = []

    for item in ranked:
        payload = _as_dict(item)
        candidate_id = payload["candidate_id"]
        predictions.append(
            integrator.evaluate(
                payload,
                pareto_map.get(candidate_id, {}),
                promo_map.get(candidate_id, {}),
            )
        )

    outputs = PredictionReport(
        ROOT / "Reports" / "ML" / "Predictions"
    ).export(predictions)

    print()
    print("CHAMPION MODEL")
    print("-" * 100)
    print("Name             :", best.model_name)
    print("Selection Score  :", best.selection_score)

    print()
    print("ML PROMOTION DECISIONS")
    print("-" * 100)

    for prediction in predictions[:10]:
        print(
            f"{prediction['candidate_id']:<24} "
            f"P={prediction['calibrated_probability']:.3f} "
            f"Conf={prediction['confidence']:.3f} "
            f"{prediction['final_action']}"
        )

    print()
    print("OUTPUT FILES")
    print("-" * 100)

    for name, path in outputs.items():
        print(f"{name:<10}: {path}")

    print("=" * 100)
    print("SPRINT 7B.4 COMPLETED")
    print("=" * 100)


if __name__ == "__main__":
    main()
