"""
BursaAI v6.0 Sprint 4D validation test.

Uses injected fake functions.
No internet or live market data required.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


import pandas as pd

from Adapters.analysis_adapters import register_analysis_adapters
from Adapters.data_adapters import register_data_adapters
from Adapters.institutional_adapters import (
    register_institutional_adapters,
)
from Framework.context import AnalysisContext
from Framework.engine_registry import EngineRegistry
from Framework.logger import FrameworkLogger
from Framework.pipeline import Pipeline
from Framework.pipeline_policy import PipelinePolicy


def fake_load_stock(symbol):
    return pd.DataFrame(
        {
            "Close": [10.0, 10.2, 10.4],
            "Volume": [1000, 1300, 1900],
        }
    )


def fake_add_indicators(data):
    enriched = data.copy()
    enriched["EMA20"] = [9.9, 10.0, 10.1]
    enriched["RSI"] = [52, 57, 61]
    enriched["OBV"] = [1000, 2300, 4200]
    enriched["OBV_MA20"] = [900, 1500, 2500]
    return enriched


def fake_calculate_score(data):
    return {
        "score": 82,
        "grade": "A",
        "trend": {
            "score": 24,
            "direction": "STRONG UPTREND",
        },
        "momentum": {
            "score": 21,
            "direction": "BULLISH",
        },
        "volume": {
            "score": 14,
            "strength": "STRONG",
        },
        "volatility": {
            "score": 10,
            "status": "STABLE",
        },
        "risk": {
            "score": 13,
            "status": "LOW",
        },
    }


def fake_score_trend(data):
    return {
        "score": 24,
        "direction": "STRONG UPTREND",
    }


def fake_score_momentum(data):
    return {
        "score": 21,
        "direction": "BULLISH",
    }


def fake_score_volume(data):
    return {
        "score": 15,
        "strength": "INSTITUTIONAL",
        "ratio": 1.75,
        "reason": [
            "Strong relative volume",
        ],
    }


def fake_apply_quality_gate(result):
    output = dict(result)
    output["QualityPenalty"] = 8
    output["TradeableScore"] = 74
    output["FinalScore"] = 74
    output["Grade"] = "B+"

    output.setdefault("score", {})
    output["score"]["quality_penalty"] = 8
    output["score"]["tradeable"] = 74
    output["score"]["final"] = 74
    output["score"]["grade"] = "B+"

    return output


def fake_apply_smart_money(data, result):
    output = dict(result)
    output["InstitutionBonus"] = 8
    output["SmartMoney"] = "EARLY"
    output["FinalScore"] = 82

    output.setdefault("score", {})
    output["score"]["institution_bonus"] = 8
    output["score"]["final"] = 82

    output.setdefault("market", {})
    output["market"]["smart_money"] = "EARLY"

    return output


def main():
    logger = FrameworkLogger(
        echo=False
    )

    registry = EngineRegistry(
        logger=logger
    )

    register_data_adapters(
        registry,
        data_loader=fake_load_stock,
        indicator_function=fake_add_indicators,
        minimum_rows=3,
        required_indicator_columns=[
            "EMA20",
            "RSI",
            "OBV",
            "OBV_MA20",
        ],
    )

    register_analysis_adapters(
        registry,
        scorer=fake_calculate_score,
        trend_function=fake_score_trend,
        momentum_function=fake_score_momentum,
    )

    register_institutional_adapters(
        registry,
        volume_function=fake_score_volume,
        quality_function=fake_apply_quality_gate,
        smart_money_function=fake_apply_smart_money,
    )

    pipeline = Pipeline(
        name="Sprint 4D Institutional Pipeline",
        registry=registry,
        policy=PipelinePolicy(
            failure_mode="stop",
            validate_dependencies=True,
            record_context_snapshot=True,
        ),
        logger=logger,
    )

    context = AnalysisContext(
        symbol="1155.KL"
    )

    report = pipeline.execute(context)

    assert report.success is True
    assert report.successful_engines == 8
    assert report.failed_engines == 0

    assert context.analysis.score.raw == 82
    assert context.analysis.score.quality_penalty == 8
    assert context.analysis.score.tradeable == 74
    assert context.analysis.score.institution_bonus == 8
    assert context.analysis.score.final == 82
    assert context.analysis.score.grade == "B+"

    assert (
        context.analysis.market.volume
        == "INSTITUTIONAL"
    )

    assert (
        context.analysis.market.smart_money
        == "EARLY"
    )

    assert (
        context.analysis.extra["volume_score"]
        == 15
    )

    assert (
        context.metadata["volume_data"]["ratio"]
        == 1.75
    )

    assert (
        context.metadata["quality_data"]["QualityPenalty"]
        == 8
    )

    assert (
        context.metadata["smart_money_data"]["SmartMoney"]
        == "EARLY"
    )

    assert registry.names() == [
        "Loader Adapter",
        "Indicator Adapter",
        "Score Adapter",
        "Trend Adapter",
        "Momentum Adapter",
        "Volume Adapter",
        "Quality Gate Adapter",
        "Smart Money Adapter",
    ]

    print("=" * 78)
    print("BURSAAI v6.0 SPRINT 4D TEST")
    print("=" * 78)
    print("Volume Adapter             : OK")
    print("Quality Gate Adapter       : OK")
    print("Smart Money Adapter        : OK")
    print("Institutional Registration : OK")
    print("Pipeline Integration       : OK")
    print("Volume Context Sync        : OK")
    print("Quality Score Sync         : OK")
    print("Institution Bonus Sync     : OK")
    print("Smart Money Context Sync   : OK")
    print("Legacy Bridge Integration  : OK")
    print("=" * 78)
    print("SPRINT 4D INSTITUTIONAL ADAPTER FOUNDATION OK")


if __name__ == "__main__":
    main()
