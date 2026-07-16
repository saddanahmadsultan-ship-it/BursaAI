from __future__ import annotations

import json
import tempfile
import unittest

from Research import (
    AIRankingEngine,
    Candidate,
    ConfidenceEngine,
    ParetoEngine,
    ParetoReportExporter,
    PerformanceMetrics,
    PromotionEngine,
    ResearchResult,
    TierGate,
)


class TestSprint7A5RC4(unittest.TestCase):

    def make_pair(
        self,
        name: str,
        seed: float,
    ):
        candidate = Candidate(
            name=name,
            strategy_name="EMA_RSI",
            parameters={
                "ema_fast": 10 + int(seed),
                "ema_slow": 50,
            },
        )

        result = ResearchResult(
            experiment_id="EXP-RC4",
            candidate_id=candidate.candidate_id,
            candidate_hash=candidate.candidate_hash,
            metrics=PerformanceMetrics(
                cagr=12 + seed,
                sharpe_ratio=1.0 + seed / 20,
                sortino_ratio=1.2 + seed / 18,
                max_drawdown=max(5, 25 - seed / 2),
                volatility=max(8, 30 - seed / 3),
                exposure=45,
                profit_factor=1.2 + seed / 35,
                recovery_factor=1.5 + seed / 15,
                total_trades=60 + int(seed),
                win_rate=55 + seed / 2,
                risk_score=65 + seed / 3,
            ),
            walk_forward_folds=[
                {
                    "fold": 1,
                    "train_return": 20 + seed,
                    "test_return": 15 + seed * 0.6,
                    "test_sharpe": 1.1 + seed / 30,
                },
                {
                    "fold": 2,
                    "train_return": 21 + seed,
                    "test_return": 16 + seed * 0.6,
                    "test_sharpe": 1.2 + seed / 30,
                },
                {
                    "fold": 3,
                    "train_return": 19 + seed,
                    "test_return": 14 + seed * 0.6,
                    "test_sharpe": 1.0 + seed / 30,
                },
            ],
            monthly_returns={
                "2025-01": 1.0 + seed / 30,
                "2025-02": 1.1 + seed / 30,
                "2025-03": 0.9 + seed / 30,
            },
            yearly_returns={
                "2023": 12 + seed,
                "2024": 13 + seed,
                "2025": 14 + seed,
            },
            equity_curve=[
                {"equity": 100000},
                {"equity": 101000 + seed * 100},
                {"equity": 102000 + seed * 200},
                {"equity": 103000 + seed * 300},
            ],
            diagnostics={
                "regime_returns": {
                    "BULL": 18 + seed,
                    "SIDEWAYS": 8 + seed / 2,
                    "BEAR": 2 + seed / 4,
                    "HIGH_VOL": 5 + seed / 3,
                }
            },
        )

        return candidate, result

    def test_confidence_engine(self):
        pair = self.make_pair("A", 10)
        ranked = AIRankingEngine().rank([pair])

        confidence = ranked[0].confidence_breakdown

        self.assertIsNotNone(confidence)
        self.assertGreater(
            confidence.overall_confidence_score,
            0,
        )

    def test_pareto_front_assignment(self):
        ranked = AIRankingEngine().rank(
            [
                self.make_pair("LOW", 2),
                self.make_pair("MID", 10),
                self.make_pair("HIGH", 20),
            ]
        )

        points = ParetoEngine().rank(ranked)

        self.assertEqual(
            min(point.front for point in points),
            1,
        )

        self.assertEqual(len(points), 3)

    def test_dominant_strategy_front_one(self):
        ranked = AIRankingEngine().rank(
            [
                self.make_pair("LOW", 1),
                self.make_pair("HIGH", 25),
            ]
        )

        points = ParetoEngine().rank(ranked)

        front_by_name = {
            item.candidate_name: next(
                point.front
                for point in points
                if point.candidate_id == item.candidate_id
            )
            for item in ranked
        }

        self.assertEqual(
            front_by_name["HIGH"],
            1,
        )

    def test_tier_gate_rejects_weak(self):
        ranked = AIRankingEngine().rank(
            [self.make_pair("WEAK", 0)]
        )

        decision = TierGate().evaluate(
            ranked[0],
            pareto_front=5,
        )

        self.assertFalse(decision.passed)

    def test_promotion_engine(self):
        ranked = AIRankingEngine().rank(
            [
                self.make_pair("A", 5),
                self.make_pair("B", 20),
            ]
        )

        points = ParetoEngine().rank(ranked)

        decisions = PromotionEngine().evaluate(
            ranked,
            points,
        )

        self.assertEqual(len(decisions), 2)
        self.assertIn(
            "action",
            decisions[0],
        )

    def test_report_export(self):
        ranked = AIRankingEngine().rank(
            [
                self.make_pair("A", 5),
                self.make_pair("B", 20),
            ]
        )

        points = ParetoEngine().rank(ranked)
        promotions = PromotionEngine().evaluate(
            ranked,
            points,
        )

        with tempfile.TemporaryDirectory() as temp:
            files = ParetoReportExporter(temp).export(
                points,
                promotions,
            )

            for path in files.values():
                self.assertTrue(path.exists())

            data = json.loads(
                files["promotion_json"].read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(len(data), 2)

    def test_confidence_in_ranking_breakdown(self):
        ranked = AIRankingEngine().rank(
            [self.make_pair("A", 10)]
        )

        self.assertEqual(
            ranked[0].breakdown.confidence_score,
            ranked[0].confidence_breakdown.overall_confidence_score,
        )

    def test_empty_pareto(self):
        self.assertEqual(
            ParetoEngine().rank([]),
            [],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
