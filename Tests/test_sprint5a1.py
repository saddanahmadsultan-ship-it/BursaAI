"""
BursaAI v6.0 Sprint 5A.1 validation test.

Uses injected fake functions.
No internet or live market data required.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


import pandas as pd

from Adapters.ai_layer_adapters import (
    register_market_regime_adapter,
)
from Adapters.analysis_adapters import (
    register_analysis_adapters,
)
from Adapters.data_adapters import (
    register_data_adapters,
)
from Adapters.institutional_adapters import (
    register_institutional_adapters,
)
from Framework.context import AnalysisContext
from Framework.engine_registry import EngineRegistry
from Framework.infrastructure import (
    build_infrastructure,
)
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
    enriched["EMA50"] = [9.7, 9.8, 9.9]
    enriched["EMA200"] = [9.3, 9.4, 9.5]
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


def fake_apply_market_regime(data, result):
    output = dict(result)

    output["MarketRegime"] = "BULLISH"
    output["RegimeScore"] = 59
    output["RegimeBonus"] = 5
    output["RegimePenalty"] = 0
    output["FinalScore"] = 87

    output.setdefault("market", {})
    output["market"]["regime"] = "BULLISH"
    output["market"]["regime_score"] = 59

    output.setdefault("score", {})
    output["score"]["regime_bonus"] = 5
    output["score"]["regime_penalty"] = 0
    output["score"]["final"] = 87

    return output


def main():
    infrastructure = build_infrastructure()

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
            "EMA50",
            "EMA200",
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

    register_market_regime_adapter(
        registry,
        regime_function=fake_apply_market_regime,
        services=infrastructure.services,
    )

    received_events = []

    def on_market_regime_completed(event):
        received_events.append(event)

    infrastructure.events.subscribe(
        "MarketRegimeCompleted",
        on_market_regime_completed,
    )

    pipeline = Pipeline(
        name="Sprint 5A.1 Market Regime Pipeline",
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
    assert report.successful_engines == 9
    assert report.failed_engines == 0

    assert (
        context.analysis.market.regime
        == "BULLISH"
    )

    assert (
        context.analysis.market.regime_score
        == 59
    )

    assert (
        context.analysis.score.regime_bonus
        == 5
    )

    assert (
        context.analysis.score.regime_penalty
        == 0
    )

    assert (
        context.analysis.score.final
        == 87
    )

    assert (
        context.metadata[
            "market_regime_data"
        ]["MarketRegime"]
        == "BULLISH"
    )

    assert len(received_events) == 1

    event = received_events[0]

    assert (
        event.name
        == "MarketRegimeCompleted"
    )

    assert (
        event.payload["symbol"]
        == "1155.KL"
    )

    assert (
        event.payload["regime"]
        == "BULLISH"
    )

    assert (
        event.payload["final_score"]
        == 87
    )

    assert registry.names()[-1] == (
        "Market Regime Adapter"
    )

    print("=" * 82)
    print("BURSAAI v6.0 SPRINT 5A.1 TEST")
    print("=" * 82)
    print("Market Regime Adapter     : OK")
    print("Legacy Engine Integration : OK")
    print("Regime Context Sync       : OK")
    print("Regime Score Sync         : OK")
    print("Regime Bonus Sync         : OK")
    print("Regime Penalty Sync       : OK")
    print("Final Score Sync          : OK")
    print("Service Container         : OK")
    print("Event Bus Publication     : OK")
    print("Pipeline Integration      : OK")
    print("=" * 82)
    print("SPRINT 5A.1 MARKET REGIME ADAPTER OK")


if __name__ == "__main__":
    main()
