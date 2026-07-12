from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from Research import (
    Candidate,
    ResearchResultStore,
    WalkForwardAdapter,
    WalkForwardAdapterConfig,
)
from Research.mock_walk_forward import (
    deterministic_mock_walk_forward,
)


class TestSprint7A4(unittest.TestCase):

    def make_candidate(self):
        return Candidate(
            name="EMA RSI Test",
            strategy_name="EMA_RSI",
            parameters={
                "ema_fast": 20,
                "ema_slow": 50,
                "rsi_period": 14,
            },
            symbol="1155.KL",
        )

    def test_adapter_success(self):
        candidate = self.make_candidate()

        adapter = WalkForwardAdapter(
            deterministic_mock_walk_forward,
            WalkForwardAdapterConfig(
                minimum_folds=3,
                require_equity_curve=True,
            ),
        )

        result = adapter.evaluate(
            "EXP-TEST",
            candidate,
        )

        self.assertTrue(result.successful)
        self.assertGreaterEqual(
            len(result.walk_forward_folds),
            3,
        )
        self.assertGreater(
            len(result.equity_curve),
            0,
        )

    def test_adapter_failure_returns_result(self):
        candidate = self.make_candidate()

        adapter = WalkForwardAdapter(
            lambda candidate: {
                "metrics": {},
                "folds": [],
            },
            WalkForwardAdapterConfig(
                minimum_folds=2,
            ),
        )

        result = adapter.evaluate(
            "EXP-TEST",
            candidate,
        )

        self.assertFalse(result.successful)
        self.assertIsNotNone(result.error_message)

    def test_evaluator_wrapper(self):
        candidate = self.make_candidate()
        captured = []

        adapter = WalkForwardAdapter(
            deterministic_mock_walk_forward
        )

        evaluator = adapter.evaluator(
            "EXP-TEST",
            result_callback=captured.append,
        )

        metrics = evaluator(candidate)

        self.assertGreater(
            metrics.final_score,
            0,
        )
        self.assertEqual(len(captured), 1)

    def test_result_store_save_load(self):
        candidate = self.make_candidate()

        adapter = WalkForwardAdapter(
            deterministic_mock_walk_forward
        )

        result = adapter.evaluate(
            "EXP-STORE",
            candidate,
        )

        with tempfile.TemporaryDirectory() as temp:
            store = ResearchResultStore(
                Path(temp) / "ResearchResults"
            )

            store.save(result)
            loaded = store.load(result.result_id)

            self.assertEqual(
                loaded.result_id,
                result.result_id,
            )
            self.assertEqual(
                loaded.candidate_hash,
                result.candidate_hash,
            )

    def test_result_store_list_filter(self):
        candidate = self.make_candidate()

        adapter = WalkForwardAdapter(
            deterministic_mock_walk_forward
        )

        with tempfile.TemporaryDirectory() as temp:
            store = ResearchResultStore(
                Path(temp) / "ResearchResults"
            )

            result = adapter.evaluate(
                "EXP-FILTER",
                candidate,
            )

            store.save(result)

            self.assertEqual(
                len(store.list(
                    experiment_id="EXP-FILTER"
                )),
                1,
            )

            self.assertEqual(
                len(store.list(
                    experiment_id="EXP-OTHER"
                )),
                0,
            )

    def test_best_result(self):
        candidate_a = self.make_candidate()

        candidate_b = Candidate(
            name="EMA RSI Test B",
            strategy_name="EMA_RSI",
            parameters={
                "ema_fast": 10,
                "ema_slow": 50,
                "rsi_period": 8,
            },
            symbol="1155.KL",
        )

        adapter = WalkForwardAdapter(
            deterministic_mock_walk_forward
        )

        with tempfile.TemporaryDirectory() as temp:
            store = ResearchResultStore(
                Path(temp) / "ResearchResults"
            )

            result_a = adapter.evaluate(
                "EXP-BEST",
                candidate_a,
            )
            result_b = adapter.evaluate(
                "EXP-BEST",
                candidate_b,
            )

            store.save(result_a)
            store.save(result_b)

            best = store.best_result("EXP-BEST")

            self.assertIsNotNone(best)
            self.assertEqual(
                best.metrics.final_score,
                max(
                    result_a.metrics.final_score,
                    result_b.metrics.final_score,
                ),
            )

    def test_checksum_tampering(self):
        candidate = self.make_candidate()

        adapter = WalkForwardAdapter(
            deterministic_mock_walk_forward
        )

        result = adapter.evaluate(
            "EXP-TAMPER",
            candidate,
        )

        with tempfile.TemporaryDirectory() as temp:
            store = ResearchResultStore(
                Path(temp) / "ResearchResults"
            )

            path = store.save(result)
            data = json.loads(
                path.read_text(encoding="utf-8")
            )

            data["metrics"]["final_score"] = 1

            path.write_text(
                json.dumps(data),
                encoding="utf-8",
            )

            with self.assertRaises(Exception):
                store.load(result.result_id)

    def test_result_delete(self):
        candidate = self.make_candidate()

        adapter = WalkForwardAdapter(
            deterministic_mock_walk_forward
        )

        result = adapter.evaluate(
            "EXP-DELETE",
            candidate,
        )

        with tempfile.TemporaryDirectory() as temp:
            store = ResearchResultStore(
                Path(temp) / "ResearchResults"
            )

            store.save(result)

            self.assertTrue(
                store.delete(result.result_id)
            )

            self.assertEqual(
                store.list(
                    experiment_id="EXP-DELETE"
                ),
                [],
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
