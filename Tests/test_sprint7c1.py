from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from TradingIntelligence import (
    PositionCandidate,
    PositionIntelligenceConfig,
    PositionIntelligenceEngine,
    PositionIntelligenceReport,
    PositionRiskProfile,
)


class TestSprint7C1(unittest.TestCase):

    def setUp(self) -> None:
        self.config = PositionIntelligenceConfig(
            portfolio_capital=100000.0,
        )
        self.engine = PositionIntelligenceEngine(
            self.config
        )
        self.profile = PositionRiskProfile(
            portfolio_capital=100000.0,
            available_capital=90000.0,
            current_portfolio_risk_percent=1.5,
            active_positions=2,
            current_drawdown_percent=2.0,
            sector_exposure_percent=10.0,
        )

    def good_candidate(self) -> PositionCandidate:
        return PositionCandidate(
            symbol="1295.KL",
            price=4.90,
            atr=0.12,
            final_score=86.0,
            confidence=88.0,
            signal="STRONG BUY",
            ml_probability=0.82,
            volatility_percent=2.1,
            sector="FINANCIAL",
            support_price=4.82,
            resistance_price=5.35,
        )

    def test_good_candidate_is_approved(self):
        plan = self.engine.build_plan(
            self.good_candidate(),
            self.profile,
        )
        self.assertTrue(plan.approved)
        self.assertGreater(plan.quantity, 0)

    def test_stop_is_below_entry(self):
        plan = self.engine.build_plan(
            self.good_candidate(),
            self.profile,
        )
        self.assertLess(
            plan.stop_loss,
            plan.entry_price,
        )

    def test_target_is_above_entry(self):
        plan = self.engine.build_plan(
            self.good_candidate(),
            self.profile,
        )
        self.assertGreater(
            plan.target_price,
            plan.entry_price,
        )

    def test_position_respects_maximum_size(self):
        plan = self.engine.build_plan(
            self.good_candidate(),
            self.profile,
        )
        self.assertLessEqual(
            plan.position_percent,
            self.config.maximum_position_percent,
        )

    def test_low_confidence_rejected(self):
        candidate = self.good_candidate()
        candidate.confidence = 40.0

        plan = self.engine.build_plan(
            candidate,
            self.profile,
        )

        self.assertFalse(plan.approved)
        self.assertEqual(
            plan.action,
            "REJECT_POSITION",
        )

    def test_hold_signal_rejected(self):
        candidate = self.good_candidate()
        candidate.signal = "HOLD"

        plan = self.engine.build_plan(
            candidate,
            self.profile,
        )

        self.assertFalse(plan.approved)

    def test_drawdown_reduces_risk(self):
        normal = self.engine.build_plan(
            self.good_candidate(),
            self.profile,
        )

        drawdown_profile = PositionRiskProfile(
            portfolio_capital=100000.0,
            available_capital=90000.0,
            current_portfolio_risk_percent=1.5,
            active_positions=2,
            current_drawdown_percent=10.0,
            sector_exposure_percent=10.0,
        )

        reduced = self.engine.build_plan(
            self.good_candidate(),
            drawdown_profile,
        )

        self.assertLess(
            reduced.risk_percent,
            normal.risk_percent,
        )

    def test_report_export(self):
        with tempfile.TemporaryDirectory() as temp:
            plan = self.engine.build_plan(
                self.good_candidate(),
                self.profile,
            )

            outputs = PositionIntelligenceReport(
                temp
            ).export([plan])

            for path in outputs.values():
                self.assertTrue(Path(path).exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
