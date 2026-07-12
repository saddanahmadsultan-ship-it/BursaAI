"""
BursaAI v6.0 Sprint 4A validation test.

Run from:
    BursaAI/
or:
    BursaAI/Tests/
"""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from Adapters.base_adapter import BaseAdapter
from Framework.context import AnalysisContext
from Framework.engine_registry import EngineRegistry
from Framework.legacy_bridge import LegacyBridge
from Framework.logger import FrameworkLogger
from Framework.metadata import EngineMetadata
from Framework.pipeline import Pipeline
from Framework.pipeline_policy import PipelinePolicy


class LegacyScoreAdapter(BaseAdapter):
    METADATA = EngineMetadata(
        name="Legacy Score Adapter",
        version="6.0",
        priority=10,
        category="adapter",
    )

    def run_legacy(self, context):
        return {
            "RawScore": 78,
            "TradeableScore": 70,
            "FinalScore": 84,
            "Grade": "A",
            "Confidence": 88,
            "ConfLevel": "HIGH",
            "Signal": "BUY",
            "Entry": 10.50,
            "StopLoss": 10.00,
            "Target": 11.50,
            "RR": 2.00,
        }


def test_flat_legacy_to_context():
    bridge = LegacyBridge()

    legacy = {
        "Code": "1155.KL",
        "Price": "RM10.50",
        "RawScore": 80,
        "FinalScore": 86,
        "Confidence": "90%",
        "Signal": "BUY",
        "CapitalUsed": "25,000",
        "Shares": 2300,
        "PortfolioStatus": "ALLOCATED",
    }

    context = bridge.legacy_to_context(
        legacy=legacy
    )

    assert context.symbol == "1155.KL"
    assert context.analysis.identity.price == 10.50
    assert context.analysis.score.final == 86
    assert context.analysis.confidence == 90
    assert context.analysis.trade.signal == "BUY"
    assert context.analysis.position.capital_used == 25000
    assert context.analysis.portfolio.status == "ALLOCATED"


def test_nested_legacy_to_context():
    bridge = LegacyBridge()

    legacy = {
        "identity": {
            "code": "1295.KL",
            "price": 4.89,
        },
        "score": {
            "raw": 84,
            "tradeable": 74,
            "final": 87,
            "grade": "A",
        },
        "confidence": {
            "value": 90,
            "level": "VERY HIGH",
        },
        "market": {
            "trend": "STRONG UPTREND",
            "regime": "BULLISH",
        },
        "trade": {
            "signal": "HOLD",
            "entry": 4.89,
            "stop_loss": 4.75,
            "target": 5.16,
            "risk_reward": 1.93,
        },
    }

    context = bridge.legacy_to_context(
        legacy=legacy
    )

    assert context.analysis.identity.code == "1295.KL"
    assert context.analysis.score.final == 87
    assert context.analysis.confidence == 90
    assert context.analysis.market.regime == "BULLISH"
    assert context.analysis.trade.signal == "HOLD"


def test_context_to_legacy_round_trip():
    bridge = LegacyBridge()

    context = AnalysisContext(
        symbol="1023.KL"
    )

    context.analysis.identity.price = 7.65
    context.analysis.score.raw = 73
    context.analysis.score.tradeable = 62
    context.analysis.score.final = 72
    context.analysis.score.grade = "B+"
    context.analysis.confidence = 79
    context.analysis.confidence_level = "HIGH"
    context.analysis.trade.signal = "WATCH"
    context.analysis.position.shares = 2700
    context.analysis.position.lots = 27
    context.analysis.position.account_capital = 100000
    context.analysis.position.capital_used = 20655
    context.analysis.position.remaining_capital = 79345
    context.analysis.portfolio.status = "ALLOCATED"
    context.analysis.portfolio.allocated_capital = 20655

    legacy = bridge.context_to_legacy(
        context
    )

    assert legacy["Code"] == "1023.KL"
    assert legacy["FinalScore"] == 72
    assert legacy["Signal"] == "WATCH"
    assert legacy["Shares"] == 2700
    assert legacy["position"]["capital_used"] == 20655
    assert legacy["portfolio"]["status"] == "ALLOCATED"

    second_context = bridge.legacy_to_context(
        legacy=legacy
    )

    assert second_context.analysis.score.final == 72
    assert second_context.analysis.position.shares == 2700
    assert (
        second_context.analysis.portfolio.allocated_capital
        == 20655
    )


def test_base_adapter_pipeline():
    logger = FrameworkLogger(
        echo=False
    )

    registry = EngineRegistry(
        logger=logger
    )

    registry.register(
        LegacyScoreAdapter()
    )

    pipeline = Pipeline(
        name="Sprint 4A Adapter Pipeline",
        registry=registry,
        policy=PipelinePolicy(
            failure_mode="stop",
            validate_dependencies=True,
        ),
        logger=logger,
    )

    context = AnalysisContext(
        symbol="1155.KL"
    )

    report = pipeline.execute(context)

    assert report.success is True
    assert report.successful_engines == 1
    assert context.analysis.score.final == 84
    assert context.analysis.trade.signal == "BUY"
    assert context.analysis.trade.risk_reward == 2.0


def main():
    test_flat_legacy_to_context()
    test_nested_legacy_to_context()
    test_context_to_legacy_round_trip()
    test_base_adapter_pipeline()

    print("=" * 72)
    print("BURSAAI v6.0 SPRINT 4A TEST")
    print("=" * 72)
    print("Base Adapter           : OK")
    print("Flat Legacy Bridge     : OK")
    print("Nested Legacy Bridge   : OK")
    print("Context to Legacy      : OK")
    print("Round Trip Conversion  : OK")
    print("Pipeline Integration   : OK")
    print("Legacy Metadata Merge  : OK")
    print("=" * 72)
    print("SPRINT 4A LEGACY ADAPTER FOUNDATION OK")


if __name__ == "__main__":
    main()
