from pathlib import Path
from MachineLearning import FeatureSchema, MLDataset, MLModelRegistry, MLTrainingPipeline, MeanThresholdClassifier

ROOT = Path(__file__).resolve().parent

def build_demo_dataset():
    schema = FeatureSchema.from_names(
        ["ai_score", "robustness", "consistency", "confidence", "risk_score"],
        "promoted",
    )
    records = []
    for index in range(80):
        promoted = index >= 40
        base = (72 + index % 18) if promoted else (35 + index % 25)
        records.append(
            {
                "ai_score": base,
                "robustness": base + 2,
                "consistency": base + 4,
                "confidence": base + 1,
                "risk_score": base - 3,
                "promoted": 1 if promoted else 0,
            }
        )
    return MLDataset.from_records(schema, records)

def main():
    print("=" * 80)
    print(" BursaAI v7 Sprint 7B.1 — Machine Learning Foundations")
    print("=" * 80)

    registry = MLModelRegistry(ROOT / "Models")
    result = MLTrainingPipeline(registry).run(
        build_demo_dataset(),
        MeanThresholdClassifier("BursaAI Promotion Baseline"),
    )
    prediction = registry.load(result.model_id).predict_one(
        [84, 88, 91, 86, 78]
    )

    print("Samples             :", result.sample_count)
    print("Model ID            :", result.model_id)
    print("Train Accuracy      :", f"{result.train_accuracy:.2%}")
    print("Validation Accuracy :", f"{result.validation_accuracy:.2%}")
    print("Test Accuracy       :", f"{result.test_accuracy:.2%}")
    print("Prediction          :", int(prediction.prediction))
    print("Probability         :", prediction.probability)
    print("Confidence          :", prediction.confidence)
    print("=" * 80)
    print("SPRINT 7B.1 COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    main()
