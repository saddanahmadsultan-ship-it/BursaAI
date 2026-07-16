from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from Research import (
    AIRankingEngine,
    Candidate,
    LeaderboardExporter,
    PerformanceMetrics,
    ResearchResult,
    RobustnessEngine,
)


class TestSprint7A5RC2(unittest.TestCase):

    def make_candidate(self, name="A", fast=10):
        return Candidate(
            name=name,
            strategy_name="EMA_RSI",
            parameters={
                "ema_fast": fast,
                "ema_slow": 50,
                "rsi_period": 14,
            },
        )

    def make_result(self, candidate, folds=None, diagnostics=None):
        return ResearchResult(
            experiment_id="EXP-RC2",
            candidate_id=candidate.candidate_id,
            candidate_hash=candidate.candidate_hash,
            metrics=PerformanceMetrics(
                cagr=20,
                sharpe_ratio=1.8,
                sortino_ratio=2.2,
                max_drawdown=12,
                volatility=18,
                exposure=55,
                profit_factor=1.7,
                recovery_factor=2.1,
                total_trades=90,
                consistency_score=78,
                robustness_score=1,
                risk_score=75,
            ),
            walk_forward_folds=folds or [
                {
                    "fold": 1,
                    "train_return": 20,
                    "test_return": 15,
                    "test_sharpe": 1.4,
                },
                {
                    "fold": 2,
                    "train_return": 21,
                    "test_return": 16,
                    "test_sharpe": 1.5,
                },
                {
                    "fold": 3,
                    "train_return": 19,
                    "test_return": 14,
                    "test_sharpe": 1.3,
                },
            ],
            diagnostics=diagnostics or {
                "regime_returns": {
                    "BULL": 18,
                    "SIDEWAYS": 9,
                    "BEAR": 3,
                }
            },
            equity_curve=[
                {"date": "2025-01-01", "equity": 100000},
                {"date": "2025-02-01", "equity": 102000},
            ],
        )

    def test_good_robustness(self):
        candidate = self.make_candidate()
        result = self.make_result(candidate)

        score = RobustnessEngine().evaluate(
            candidate,
            result,
        )

        self.assertGreater(
            score.overall_robustness_score,
            60,
        )

    def test_bad_fold_success(self):
        candidate = self.make_candidate()
        result = self.make_result(
            candidate,
            folds=[
                {
                    "fold": 1,
                    "train_return": 20,
                    "test_return": -10,
                    "test_sharpe": -1,
                },
                {
                    "fold": 2,
                    "train_return": 18,
                    "test_return": -5,
                    "test_sharpe": -0.5,
                },
            ],
        )

        score = RobustnessEngine().evaluate(
            candidate,
            result,
        )

        self.assertEqual(
            score.fold_success_score,
            0.0,
        )

    def test_high_degradation_penalized(self):
        candidate = self.make_candidate()

        good = self.make_result(
            candidate,
            folds=[
                {
                    "fold": 1,
                    "train_return": 20,
                    "test_return": 18,
                    "test_sharpe": 1,
                }
            ],
        )

        bad = self.make_result(
            candidate,
            folds=[
                {
                    "fold": 1,
                    "train_return": 20,
                    "test_return": 2,
                    "test_sharpe": 1,
                }
            ],
        )

        engine = RobustnessEngine()

        self.assertGreater(
            engine.evaluate(candidate, good).degradation_score,
            engine.evaluate(candidate, bad).degradation_score,
        )

    def test_dispersion_penalty(self):
        candidate = self.make_candidate()

        stable = self.make_result(
            candidate,
            folds=[
                {"fold": 1, "train_return": 12, "test_return": 10, "test_sharpe": 1},
                {"fold": 2, "train_return": 12, "test_return": 11, "test_sharpe": 1},
                {"fold": 3, "train_return": 12, "test_return": 9, "test_sharpe": 1},
            ],
        )

        unstable = self.make_result(
            candidate,
            folds=[
                {"fold": 1, "train_return": 12, "test_return": 25, "test_sharpe": 1},
                {"fold": 2, "train_return": 12, "test_return": -5, "test_sharpe": 1},
                {"fold": 3, "train_return": 12, "test_return": 1, "test_sharpe": 1},
            ],
        )

        engine = RobustnessEngine()

        self.assertGreater(
            engine.evaluate(candidate, stable).fold_dispersion_score,
            engine.evaluate(candidate, unstable).fold_dispersion_score,
        )

    def test_parameter_stability(self):
        candidate = self.make_candidate("A", 10)
        peer_close = self.make_candidate("B", 12)
        peer_far = self.make_candidate("C", 40)
        result = self.make_result(candidate)

        engine = RobustnessEngine()

        close_score = engine.evaluate(
            candidate,
            result,
            [candidate, peer_close],
        ).parameter_stability_score

        far_score = engine.evaluate(
            candidate,
            result,
            [candidate, peer_far],
        ).parameter_stability_score

        self.assertGreater(close_score, far_score)

    def test_ranking_uses_computed_robustness(self):
        candidate = self.make_candidate()
        result = self.make_result(candidate)

        ranked = AIRankingEngine().rank(
            [(candidate, result)]
        )

        self.assertNotEqual(
            ranked[0].breakdown.robustness_score,
            1,
        )

        self.assertIsNotNone(
            ranked[0].robustness_breakdown
        )

    def test_export_contains_robustness(self):
        candidate = self.make_candidate()
        result = self.make_result(candidate)

        ranked = AIRankingEngine().rank(
            [(candidate, result)]
        )

        with tempfile.TemporaryDirectory() as temp:
            files = LeaderboardExporter(temp).export_all(
                ranked
            )

            data = json.loads(
                files["json"].read_text(
                    encoding="utf-8"
                )
            )

            self.assertIn(
                "robustness_breakdown",
                data[0],
            )

    def test_empty_folds(self):
        candidate = self.make_candidate()
        result = self.make_result(candidate, folds=[])
        result.walk_forward_folds = []

        score = RobustnessEngine().evaluate(
            candidate,
            result,
        )

        self.assertEqual(
            score.fold_success_score,
            0.0,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
