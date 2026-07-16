from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from MachineLearning import (
    DatasetExporter,
    FeaturePipelineConfig,
    ResearchDatasetBuilder,
    ResearchDatasetValidator,
    ResearchFeatureEngineer,
    ResearchFeaturePipeline,
    ResearchLabelBuilder,
    StandardFeatureScaler,
)


class TestSprint7B2(unittest.TestCase):

    def make_inputs(self):
        ranked = []
        pareto = []
        promotions = []

        for index in range(12):
            strong = index < 5
            candidate_id = f"C-{index:03d}"

            overall = 82 - index if strong else 62 - index
            robustness = 86 - index if strong else 58 - index
            consistency = 88 - index if strong else 60 - index
            confidence = 84 - index if strong else 55 - index

            ranked.append(
                {
                    "rank": index + 1,
                    "candidate_id": candidate_id,
                    "candidate_name": f"STRATEGY_{index:03d}",
                    "experiment_id": "EXP-7B2",
                    "strategy_name": "EMA_RSI_ATR",
                    "tier": (
                        "RESEARCH_SILVER"
                        if strong
                        else "EXPERIMENTAL"
                    ),
                    "recommendation": (
                        "ADVANCE_TO_STRESS_TEST"
                        if strong
                        else "REVIEW_AND_RETUNE"
                    ),
                    "breakdown": {
                        "overall_score": overall,
                        "performance_score": overall - 3,
                        "risk_score": 75 if strong else 48,
                        "consistency_score": consistency,
                        "robustness_score": robustness,
                        "confidence_score": confidence,
                    },
                    "metrics": {
                        "cagr": 22 if strong else 7,
                        "sharpe_ratio": 1.8 if strong else 0.5,
                        "sortino_ratio": 2.2 if strong else 0.7,
                        "max_drawdown": 12 if strong else 31,
                        "volatility": 17 if strong else 36,
                        "profit_factor": 1.8 if strong else 1.05,
                        "recovery_factor": 2.2 if strong else 0.4,
                        "win_rate": 61 if strong else 43,
                        "total_trades": 110 if strong else 35,
                    },
                }
            )

            pareto.append(
                {
                    "candidate_id": candidate_id,
                    "front": 1 if strong else 4,
                    "crowding_distance": 1.5 + index / 10,
                }
            )

            promotions.append(
                {
                    "candidate_id": candidate_id,
                    "approved_tier": (
                        "RESEARCH_SILVER"
                        if strong
                        else "EXPERIMENTAL"
                    ),
                    "action": (
                        "ADVANCE_TO_STRESS_TEST"
                        if strong
                        else "REVIEW_AND_RETUNE"
                    ),
                }
            )

        return ranked, pareto, promotions

    def test_feature_engineering(self):
        features = ResearchFeatureEngineer().transform(
            {
                "overall_score": 80,
                "performance_score": 75,
                "risk_score": 70,
                "consistency_score": 85,
                "robustness_score": 88,
                "confidence_score": 82,
                "cagr": 20,
                "max_drawdown": 10,
                "volatility": 18,
                "total_trades": 100,
                "pareto_front": 1,
                "crowding_distance": 2,
            }
        )

        self.assertIn(
            "quality_composite",
            features,
        )

        self.assertGreater(
            features["return_drawdown_ratio"],
            0,
        )

    def test_label_builder(self):
        label = ResearchLabelBuilder().build(
            {
                "promotion_action": "ADVANCE_TO_STRESS_TEST",
                "overall_score": 80,
                "confidence_score": 75,
            }
        )

        self.assertEqual(label, 1.0)

    def test_dataset_builder(self):
        ranked, pareto, promotions = self.make_inputs()

        dataset = ResearchDatasetBuilder().build(
            ranked,
            pareto,
            promotions,
        )

        self.assertEqual(dataset.size, 12)
        self.assertEqual(
            sum(dataset.targets),
            5.0,
        )
        self.assertGreater(
            len(dataset.feature_names),
            20,
        )

    def test_dataset_validation(self):
        ranked, pareto, promotions = self.make_inputs()

        dataset = ResearchDatasetBuilder().build(
            ranked,
            pareto,
            promotions,
        )

        report = ResearchDatasetValidator().validate(
            dataset
        )

        self.assertTrue(report.passed)
        self.assertEqual(
            report.positive_count,
            5,
        )

    def test_scaler(self):
        rows = [
            {"a": 1.0, "b": 3.0},
            {"a": 2.0, "b": 5.0},
            {"a": 3.0, "b": 7.0},
        ]

        scaler = StandardFeatureScaler()
        scaler.fit(rows)
        transformed = scaler.transform(rows)

        self.assertAlmostEqual(
            sum(row["a"] for row in transformed),
            0.0,
            places=6,
        )

    def test_exporter(self):
        ranked, pareto, promotions = self.make_inputs()
        dataset = ResearchDatasetBuilder().build(
            ranked,
            pareto,
            promotions,
        )
        validation = ResearchDatasetValidator().validate(
            dataset
        )

        with tempfile.TemporaryDirectory() as temp:
            outputs = DatasetExporter(temp).export_all(
                dataset,
                validation,
            )

            self.assertTrue(outputs["csv"].exists())
            self.assertTrue(outputs["json"].exists())
            self.assertTrue(outputs["summary"].exists())

            summary = json.loads(
                outputs["summary"].read_text(
                    encoding="utf-8"
                )
            )

            self.assertTrue(
                summary["validation"]["passed"]
            )

    def test_full_feature_pipeline(self):
        ranked, pareto, promotions = self.make_inputs()

        with tempfile.TemporaryDirectory() as temp:
            pipeline = ResearchFeaturePipeline(
                FeaturePipelineConfig(
                    output_dir=Path(temp),
                )
            )

            result = pipeline.run(
                ranked,
                pareto,
                promotions,
            )

            self.assertTrue(
                result["validation"].passed
            )

            self.assertEqual(
                result["dataset"].size,
                12,
            )

    def test_duplicate_detection(self):
        ranked, pareto, promotions = self.make_inputs()

        duplicate_ranked = [
            ranked[0],
            dict(ranked[0]),
        ]

        duplicate_pareto = [
            pareto[0],
            pareto[0],
        ]

        duplicate_promotions = [
            promotions[0],
            promotions[0],
        ]

        dataset = ResearchDatasetBuilder().build(
            duplicate_ranked,
            duplicate_pareto,
            duplicate_promotions,
        )

        report = ResearchDatasetValidator().validate(
            dataset
        )

        self.assertFalse(report.passed)
        self.assertEqual(
            report.duplicate_count,
            1,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
