"""
=========================================================
BursaAI Sprint 7A.1 Test Suite
Research Models and Parameter Space
=========================================================
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest

from pathlib import Path


# =========================================================
# ENSURE PROJECT ROOT AVAILABLE
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from Research import (  # noqa: E402
    Candidate,
    CandidateStatus,
    Experiment,
    ExperimentStatus,
    ParameterSpace,
    PerformanceMetrics,
    ResearchResult,
)


class TestPerformanceMetrics(unittest.TestCase):

    def test_metrics_creation(self):
        metrics = PerformanceMetrics(
            cagr=18.5,
            sharpe_ratio=1.82,
            max_drawdown=-12.4,
            win_rate=61.2,
            total_trades=100,
            winning_trades=61,
            losing_trades=39,
            final_score=88.5,
        )

        self.assertEqual(metrics.max_drawdown, 12.4)
        self.assertEqual(metrics.win_rate, 61.2)
        self.assertEqual(metrics.final_score, 88.5)
        self.assertTrue(metrics.validate_trade_counts())

    def test_metrics_clamping(self):
        metrics = PerformanceMetrics(
            win_rate=120,
            exposure=-10,
            final_score=150,
            risk_score=-20,
        )

        self.assertEqual(metrics.win_rate, 100.0)
        self.assertEqual(metrics.exposure, 0.0)
        self.assertEqual(metrics.final_score, 100.0)
        self.assertEqual(metrics.risk_score, 0.0)

    def test_metrics_serialization(self):
        metrics = PerformanceMetrics(
            cagr=20,
            sharpe_ratio=2.0,
            final_score=90,
        )

        restored = PerformanceMetrics.from_dict(
            metrics.to_dict()
        )

        self.assertEqual(restored.cagr, 20.0)
        self.assertEqual(restored.sharpe_ratio, 2.0)
        self.assertEqual(restored.final_score, 90.0)


class TestCandidate(unittest.TestCase):

    def test_candidate_hash_is_stable(self):
        candidate_a = Candidate(
            name="Candidate A",
            strategy_name="EMA_RSI",
            parameters={
                "ema_fast": 20,
                "ema_slow": 50,
                "rsi_period": 14,
            },
            symbol="1155.KL",
        )

        candidate_b = Candidate(
            name="Candidate B",
            strategy_name="EMA_RSI",
            parameters={
                "rsi_period": 14,
                "ema_slow": 50,
                "ema_fast": 20,
            },
            symbol="1155.KL",
        )

        self.assertNotEqual(
            candidate_a.candidate_id,
            candidate_b.candidate_id,
        )

        self.assertEqual(
            candidate_a.candidate_hash,
            candidate_b.candidate_hash,
        )

    def test_candidate_different_parameters_have_different_hash(self):
        candidate_a = Candidate(
            name="A",
            strategy_name="EMA_RSI",
            parameters={
                "ema_fast": 20,
                "ema_slow": 50,
            },
        )

        candidate_b = Candidate(
            name="B",
            strategy_name="EMA_RSI",
            parameters={
                "ema_fast": 10,
                "ema_slow": 50,
            },
        )

        self.assertNotEqual(
            candidate_a.candidate_hash,
            candidate_b.candidate_hash,
        )

    def test_candidate_lifecycle(self):
        candidate = Candidate(
            name="Lifecycle Test",
            strategy_name="EMA_RSI",
            parameters={"rsi_period": 14},
        )

        self.assertEqual(
            candidate.status,
            CandidateStatus.PENDING,
        )

        candidate.mark_queued()

        self.assertEqual(
            candidate.status,
            CandidateStatus.QUEUED,
        )

        candidate.mark_running()

        self.assertEqual(
            candidate.status,
            CandidateStatus.RUNNING,
        )

        candidate.mark_completed(
            PerformanceMetrics(
                cagr=21.0,
                final_score=91.0,
            )
        )

        self.assertEqual(
            candidate.status,
            CandidateStatus.COMPLETED,
        )

        self.assertTrue(candidate.is_terminal())
        self.assertTrue(candidate.is_successful())
        self.assertEqual(candidate.metrics.final_score, 91.0)

    def test_candidate_serialization(self):
        candidate = Candidate(
            name="Serialization Test",
            strategy_name="EMA_RSI",
            parameters={
                "ema_fast": 20,
                "ema_slow": 50,
            },
            symbol="1295.KL",
            tags=["trend", "research"],
        )

        candidate.mark_completed(
            PerformanceMetrics(
                cagr=19.0,
                sharpe_ratio=1.8,
                final_score=87.0,
            )
        )

        payload = candidate.to_dict()
        restored = Candidate.from_dict(payload)

        self.assertEqual(
            restored.candidate_id,
            candidate.candidate_id,
        )

        self.assertEqual(
            restored.candidate_hash,
            candidate.candidate_hash,
        )

        self.assertEqual(
            restored.metrics.final_score,
            87.0,
        )

    def test_candidate_hash_tampering_detection(self):
        candidate = Candidate(
            name="Security Test",
            strategy_name="EMA_RSI",
            parameters={"rsi_period": 14},
        )

        payload = candidate.to_dict()

        payload["parameters"]["rsi_period"] = 8

        with self.assertRaises(ValueError):
            Candidate.from_dict(payload)


class TestParameterSpace(unittest.TestCase):

    def test_total_combinations(self):
        space = ParameterSpace(
            strategy_name="EMA_RSI_ATR",
            parameters={
                "ema_fast": [10, 20],
                "ema_slow": [50, 100],
                "rsi_period": [8, 14],
                "atr_multiplier": [1.5, 2.0],
            },
        )

        self.assertEqual(
            space.total_combinations,
            16,
        )

    def test_grid_generation_with_constraints(self):
        space = ParameterSpace(
            strategy_name="EMA_CROSS",
            parameters={
                "ema_fast": [10, 20, 50],
                "ema_slow": [20, 50],
            },
        )

        candidates = space.generate_grid_candidates()

        # Valid:
        # 10 < 20
        # 10 < 50
        # 20 < 50
        # 50 tidak lebih kecil daripada 20 atau 50
        self.assertEqual(len(candidates), 3)

        for candidate in candidates:
            self.assertLess(
                candidate.parameters["ema_fast"],
                candidate.parameters["ema_slow"],
            )

    def test_grid_candidate_hash_uniqueness(self):
        space = ParameterSpace(
            strategy_name="RSI",
            parameters={
                "rsi_period": [8, 10, 14, 18],
            },
        )

        candidates = space.generate_grid_candidates()

        hashes = {
            candidate.candidate_hash
            for candidate in candidates
        }

        self.assertEqual(
            len(hashes),
            len(candidates),
        )

    def test_random_generation_is_reproducible(self):
        space = ParameterSpace(
            strategy_name="RSI_ATR",
            parameters={
                "rsi_period": [8, 10, 14, 18],
                "atr_multiplier": [1.5, 2.0, 2.5],
            },
        )

        sample_a = space.generate_random_candidates(
            sample_size=4,
            seed=42,
        )

        sample_b = space.generate_random_candidates(
            sample_size=4,
            seed=42,
        )

        hashes_a = [
            candidate.candidate_hash
            for candidate in sample_a
        ]

        hashes_b = [
            candidate.candidate_hash
            for candidate in sample_b
        ]

        self.assertEqual(hashes_a, hashes_b)

    def test_max_candidates(self):
        space = ParameterSpace(
            strategy_name="RSI",
            parameters={
                "rsi_period": list(range(5, 30)),
            },
        )

        candidates = space.generate_grid_candidates(
            max_candidates=5
        )

        self.assertEqual(len(candidates), 5)


class TestExperiment(unittest.TestCase):

    def build_experiment(self):
        space = ParameterSpace(
            strategy_name="EMA_RSI",
            parameters={
                "ema_fast": [10, 20],
                "ema_slow": [50],
                "rsi_period": [8, 14],
            },
        )

        candidates = space.generate_grid_candidates(
            symbol="1155.KL"
        )

        return Experiment(
            name="EMA RSI Optimization",
            description="Sprint 7A.1 test experiment",
            candidates=candidates,
            symbols=["1155.KL"],
        )

    def test_experiment_creation(self):
        experiment = self.build_experiment()

        self.assertEqual(
            experiment.status,
            ExperimentStatus.CREATED,
        )

        self.assertEqual(
            experiment.total_candidates,
            4,
        )

    def test_experiment_lifecycle(self):
        experiment = self.build_experiment()

        experiment.start()

        self.assertEqual(
            experiment.status,
            ExperimentStatus.RUNNING,
        )

        for index, candidate in enumerate(
            experiment.candidates,
            start=1,
        ):
            candidate.mark_running()

            candidate.mark_completed(
                PerformanceMetrics(
                    cagr=10 + index,
                    final_score=70 + index,
                )
            )

        experiment.finalize()

        self.assertEqual(
            experiment.status,
            ExperimentStatus.COMPLETED,
        )

        self.assertEqual(
            experiment.progress_percentage(),
            100.0,
        )

    def test_best_candidate(self):
        experiment = self.build_experiment()
        experiment.start()

        scores = [75, 91, 82, 88]

        for candidate, score in zip(
            experiment.candidates,
            scores,
        ):
            candidate.mark_running()

            candidate.mark_completed(
                PerformanceMetrics(
                    final_score=score,
                )
            )

        best = experiment.best_candidate()

        self.assertIsNotNone(best)
        self.assertEqual(
            best.metrics.final_score,
            91.0,
        )

    def test_duplicate_candidate_rejected(self):
        experiment = self.build_experiment()

        duplicate = experiment.candidates[0].clone()

        added = experiment.add_candidate(duplicate)

        self.assertFalse(added)

    def test_json_save_and_load(self):
        experiment = self.build_experiment()

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = (
                Path(temp_dir)
                / "experiment_test.json"
            )

            saved_path = experiment.save_json(file_path)

            self.assertTrue(saved_path.exists())

            restored = Experiment.load_json(saved_path)

            self.assertEqual(
                restored.experiment_id,
                experiment.experiment_id,
            )

            self.assertEqual(
                restored.total_candidates,
                experiment.total_candidates,
            )

            self.assertEqual(
                restored.candidates[0].candidate_hash,
                experiment.candidates[0].candidate_hash,
            )

            json.loads(
                saved_path.read_text(
                    encoding="utf-8"
                )
            )


class TestResearchResult(unittest.TestCase):

    def test_result_serialization(self):
        candidate = Candidate(
            name="Result Candidate",
            strategy_name="EMA_RSI",
            parameters={
                "ema_fast": 20,
                "ema_slow": 50,
            },
        )

        result = ResearchResult(
            experiment_id="EXP-TEST001",
            candidate_id=candidate.candidate_id,
            candidate_hash=candidate.candidate_hash,
            metrics=PerformanceMetrics(
                cagr=25.5,
                sharpe_ratio=2.1,
                final_score=93.0,
            ),
            walk_forward_folds=[
                {
                    "fold": 1,
                    "train_return": 15.0,
                    "test_return": 8.0,
                }
            ],
            yearly_returns={
                "2024": 18.0,
                "2025": 22.0,
            },
            execution_seconds=2.5,
        )

        restored = ResearchResult.from_dict(
            result.to_dict()
        )

        self.assertEqual(
            restored.candidate_hash,
            result.candidate_hash,
        )

        self.assertEqual(
            restored.metrics.final_score,
            93.0,
        )

        self.assertEqual(
            len(restored.walk_forward_folds),
            1,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)