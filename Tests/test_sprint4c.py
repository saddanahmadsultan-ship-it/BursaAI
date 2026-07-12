"""
BursaAI v6.0 Sprint 4C validation test.

Uses injected fake legacy functions.
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
from Framework.context import AnalysisContext
from Framework.engine_registry import EngineRegistry
from Framework.logger import FrameworkLogger
from Framework.pipeline import Pipeline
from Framework.pipeline_policy import PipelinePolicy


def fake_load_stock(symbol):
    return pd.DataFrame(
        {
            "Close": [10.0, 10.2, 10.4],
            "Volume": [1000, 1200, 1500],
        }
    )


def fake_add_indicators(data):
    enriched = data.copy()

    enriched["EMA20"] = [
        9.9,
        10.0,
        10.1,
    ]

    enriched["RSI"] = [
        52,
        57,
        61,
    ]

    return enriched


def fake_calculate_score(data):
    assert "EMA20" in data.columns

    return {
        "score": 78,
        "grade": "A",
        "trend": {
            "score": 22,
            "direction": "STRONG UPTREND",
        },
        "momentum": {
            "score": 20,
            "direction": "BULLISH",
        },
        "volume": {
            "score": 12,
            "strength": "STRONG",
        },
        "volatility": {
            "score": 10,
            "status": "STABLE",
        },
        "risk": {
            "score": 14,
            "status": "LOW",
        },
    }


def fake_score_trend(data):
    return {
        "score": 24,
        "direction": "STRONG UPTREND",
        "reason": [
            "EMA alignment",
        ],
    }


def fake_score_momentum(data):
    return {
        "score": 21,
        "direction": "BULLISH",
        "reason": [
            "Positive momentum",
        ],
    }


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
        ],
    )

    register_analysis_adapters(
        registry,
        scorer=fake_calculate_score,
        trend_function=fake_score_trend,
        momentum_function=fake_score_momentum,
    )

    pipeline = Pipeline(
        name="Sprint 4C Analysis Pipeline",
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
    assert report.successful_engines == 5
    assert report.failed_engines == 0

    assert context.analysis.score.raw == 78
    assert context.analysis.score.grade == "A"

    assert (
        context.analysis.market.trend
        == "STRONG UPTREND"
    )

    assert (
        context.analysis.market.momentum
        == "BULLISH"
    )

    assert (
        context.analysis.market.volume
        == "STRONG"
    )

    assert (
        context.analysis.market.volatility
        == "STABLE"
    )

    assert (
        context.analysis.extra["trend_score"]
        == 24
    )

    assert (
        context.analysis.extra["momentum_score"]
        == 21
    )

    assert (
        context.metadata["score_data"]["score"]
        == 78
    )

    assert (
        context.metadata["trend_data"]["score"]
        == 24
    )

    assert (
        context.metadata["momentum_data"]["score"]
        == 21
    )

    assert registry.names() == [
        "Loader Adapter",
        "Indicator Adapter",
        "Score Adapter",
        "Trend Adapter",
        "Momentum Adapter",
    ]

    print("=" * 76)
    print("BURSAAI v6.0 SPRINT 4C TEST")
    print("=" * 76)
    print("Score Adapter            : OK")
    print("Trend Adapter            : OK")
    print("Momentum Adapter         : OK")
    print("Analysis Registration    : OK")
    print("Pipeline Integration     : OK")
    print("Legacy Score Preservation: OK")
    print("Trend Context Sync       : OK")
    print("Momentum Context Sync    : OK")
    print("Volume Context Sync      : OK")
    print("Volatility Context Sync  : OK")
    print("=" * 76)
    print("SPRINT 4C ANALYSIS ADAPTER FOUNDATION OK")


if __name__ == "__main__":
    main()
