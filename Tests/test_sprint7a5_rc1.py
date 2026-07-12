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
    RankingWeights,
    ResearchResult,
)


class TestSprint7A5RC1(unittest.TestCase):

    def make_pair(
        self,
        name: str,
        score_seed: float,
    ):
        candidate = Candidate(
            name=name,
            strategy_name="EMA_RSI",
            parameters={
                "ema_fast": 10 + int(score_seed),
                "ema_slow": 50,
            },
        )

        result = ResearchResult(
            experiment_id="EXP-RANK",
            candidate_id=candidate.candidate_id,
            candidate_hash=candidate.candidate_hash,
            metrics=PerformanceMetrics(
                cagr=10 + score_seed,
                sharpe_ratio=1.0 + score_seed / 20,
                sortino_ratio=1.2 + score_seed / 18,
                max_drawdown=max(5, 25 - score_seed / 2),
                volatility=max(8, 30 - score_seed / 3),
                exposure=50,
                profit_factor=1.1 + score_seed / 40,
                recovery_factor=1.5 + score_seed / 15,
                total_trades=50 + int(score_seed),
                consistency_score=55 + score_seed,
                robustness_score=58 + score_seed,
                risk_score=60 + score_seed / 2,
            ),
            walk_forward_folds=[
                {"fold": index}
                for index in range(1, 6)
            ],
            equity_curve=[
                {"date": "2025-01-01", "equity": 100000},
                {"date": "2025-02-01", "equity": 101000},
            ],
            diagnostics={"ok": True},
        )

        return candidate, result

    def test_weights_normalized(self):
        weights = RankingWeights(
            performance=35,
            risk=20,
            consistency=20,
            robustness=20,
            confidence=5,
        )

        total = (
            weights.performance
            + weights.risk
            + weights.consistency
            + weights.robustness
            + weights.confidence
        )

        self.assertAlmostEqual(total, 1.0)

    def test_ranking_order(self):
        engine = AIRankingEngine()

        low = self.make_pair("LOW", 5)
        high = self.make_pair("HIGH", 25)

        ranked = engine.rank([low, high])

        self.assertEqual(ranked[0].candidate_name, "HIGH")
        self.assertEqual(ranked[0].rank, 1)
        self.assertEqual(ranked[1].rank, 2)

    def test_score_range(self):
        engine = AIRankingEngine()

        candidate, result = self.make_pair("RANGE", 15)
        score = engine.score(candidate, result)

        self.assertGreaterEqual(score.overall_score, 0)
        self.assertLessEqual(score.overall_score, 100)

    def test_tier_classification(self):
        engine = AIRankingEngine()

        self.assertEqual(engine.classify_tier(92), "RESEARCH_GOLD")
        self.assertEqual(engine.classify_tier(85), "RESEARCH_SILVER")
        self.assertEqual(engine.classify_tier(75), "CANDIDATE")
        self.assertEqual(engine.classify_tier(60), "EXPERIMENTAL")
        self.assertEqual(engine.classify_tier(40), "REJECT")

    def test_recommendation(self):
        engine = AIRankingEngine()

        self.assertEqual(
            engine.recommendation(92),
            "PRIORITY_VALIDATION",
        )

        self.assertEqual(
            engine.recommendation(40),
            "DO_NOT_ADVANCE",
        )

    def test_export_files(self):
        engine = AIRankingEngine()

        ranked = engine.rank(
            [
                self.make_pair("A", 10),
                self.make_pair("B", 20),
            ]
        )

        with tempfile.TemporaryDirectory() as temp:
            exporter = LeaderboardExporter(temp)
            files = exporter.export_all(ranked)

            self.assertTrue(files["json"].exists())
            self.assertTrue(files["csv"].exists())
            self.assertTrue(files["summary"].exists())

            data = json.loads(
                files["summary"].read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(data["total_ranked"], 2)
            self.assertEqual(
                data["top_candidate"]["rank"],
                1,
            )

    def test_deterministic_ranking(self):
        engine = AIRankingEngine()

        items = [
            self.make_pair("A", 15),
            self.make_pair("B", 25),
            self.make_pair("C", 5),
        ]

        first = [
            item.candidate_id
            for item in engine.rank(items)
        ]

        second = [
            item.candidate_id
            for item in engine.rank(items)
        ]

        self.assertEqual(first, second)

    def test_empty_ranking(self):
        engine = AIRankingEngine()
        self.assertEqual(engine.rank([]), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
