from __future__ import annotations

import json
import tempfile
import unittest

from Research import (
    AIRankingEngine,
    Candidate,
    ConsistencyEngine,
    LeaderboardExporter,
    PerformanceMetrics,
    ResearchResult,
)


class TestSprint7A5RC3(unittest.TestCase):

    def make_candidate(self):
        return Candidate(
            name="EMA RSI Consistency",
            strategy_name="EMA_RSI",
            parameters={
                "ema_fast": 10,
                "ema_slow": 50,
                "rsi_period": 14,
            },
        )

    def make_result(
        self,
        candidate,
        folds=None,
        monthly=None,
        yearly=None,
        equity=None,
    ):
        return ResearchResult(
            experiment_id="EXP-RC3",
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
                win_rate=62,
                consistency_score=1,
                robustness_score=75,
                risk_score=75,
            ),
            walk_forward_folds=folds or [
                {"fold": 1, "test_return": 10, "test_sharpe": 1.2},
                {"fold": 2, "test_return": 11, "test_sharpe": 1.3},
                {"fold": 3, "test_return": 9, "test_sharpe": 1.1},
            ],
            monthly_returns=monthly or {
                "2025-01": 1.0,
                "2025-02": 1.2,
                "2025-03": 0.9,
            },
            yearly_returns=yearly or {
                "2023": 12,
                "2024": 14,
                "2025": 13,
            },
            equity_curve=equity or [
                {"date": "2025-01-01", "equity": 100000},
                {"date": "2025-02-01", "equity": 101000},
                {"date": "2025-03-01", "equity": 102100},
                {"date": "2025-04-01", "equity": 103000},
            ],
            diagnostics={"ok": True},
        )

    def test_good_consistency(self):
        candidate = self.make_candidate()
        result = self.make_result(candidate)

        score = ConsistencyEngine().evaluate(result)

        self.assertGreater(
            score.overall_consistency_score,
            60,
        )

    def test_fold_instability_penalty(self):
        candidate = self.make_candidate()

        stable = self.make_result(
            candidate,
            folds=[
                {"fold": 1, "test_return": 10},
                {"fold": 2, "test_return": 11},
                {"fold": 3, "test_return": 9},
            ],
        )

        unstable = self.make_result(
            candidate,
            folds=[
                {"fold": 1, "test_return": 25},
                {"fold": 2, "test_return": -10},
                {"fold": 3, "test_return": 1},
            ],
        )

        engine = ConsistencyEngine()

        self.assertGreater(
            engine.evaluate(stable).fold_consistency_score,
            engine.evaluate(unstable).fold_consistency_score,
        )

    def test_monthly_negative_penalty(self):
        candidate = self.make_candidate()

        good = self.make_result(
            candidate,
            monthly={
                "2025-01": 1,
                "2025-02": 1.2,
                "2025-03": 0.8,
            },
        )

        bad = self.make_result(
            candidate,
            monthly={
                "2025-01": 5,
                "2025-02": -4,
                "2025-03": 1,
            },
        )

        engine = ConsistencyEngine()

        self.assertGreater(
            engine.evaluate(good).monthly_stability_score,
            engine.evaluate(bad).monthly_stability_score,
        )

    def test_equity_smoothness(self):
        candidate = self.make_candidate()

        smooth = self.make_result(
            candidate,
            equity=[
                {"equity": 100},
                {"equity": 101},
                {"equity": 102},
                {"equity": 103},
            ],
        )

        rough = self.make_result(
            candidate,
            equity=[
                {"equity": 100},
                {"equity": 120},
                {"equity": 90},
                {"equity": 110},
            ],
        )

        engine = ConsistencyEngine()

        self.assertGreater(
            engine.evaluate(smooth).equity_smoothness_score,
            engine.evaluate(rough).equity_smoothness_score,
        )

    def test_ranking_uses_computed_consistency(self):
        candidate = self.make_candidate()
        result = self.make_result(candidate)

        ranked = AIRankingEngine().rank(
            [(candidate, result)]
        )

        self.assertNotEqual(
            ranked[0].breakdown.consistency_score,
            1,
        )

        self.assertIsNotNone(
            ranked[0].consistency_breakdown
        )

    def test_export_contains_consistency(self):
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
                "consistency_breakdown",
                data[0],
            )

    def test_empty_sources(self):
        candidate = self.make_candidate()
        result = self.make_result(
            candidate,
            folds=[],
            monthly={},
            yearly={},
            equity=[],
        )

        result.walk_forward_folds = []
        result.monthly_returns = {}
        result.yearly_returns = {}
        result.equity_curve = []

        score = ConsistencyEngine().evaluate(result)

        self.assertEqual(
            score.fold_consistency_score,
            0.0,
        )

        self.assertEqual(
            score.monthly_stability_score,
            0.0,
        )

    def test_reliability_uses_win_rate(self):
        candidate = self.make_candidate()

        high = self.make_result(candidate)
        high.metrics.win_rate = 80

        low = self.make_result(candidate)
        low.metrics.win_rate = 20

        engine = ConsistencyEngine()

        self.assertGreater(
            engine.evaluate(high).return_reliability_score,
            engine.evaluate(low).return_reliability_score,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
