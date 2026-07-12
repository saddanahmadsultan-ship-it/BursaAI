"""
BursaAI v6.0 Sprint 5A.2 validation test.

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
    register_ai_layer_adapters,
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
    enriched["VWAP"] = [9.95, 10.05, 10.15]
    enriched["ATR"] = [0.18, 0.20, 0.22]
    enriched["RSI"] = [52, 57, 61]
    enriched["STOCH"] = [55, 62, 68]
    enriched["MACD_HISTOGRAM"] = [0.02, 0.04, 0.06]
    enriched["EMA20_SLOPE"] = [0.01, 0.02, 0.03]
    enriched["HIGHER_LOW"] = [False, True, True]
    enriched["HIGHER_HIGH"] = [False, True, True]
    enriched["BREAKOUT"] = [False, False, True]
    enriched["BREAKDOWN"] = [False, False, False]
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


def fake_apply_entry_timing(data, result):
    output = dict(result)

    output["EntryTimingScore"] = 84
    output["EntryTimingStatus"] = "READY"
    output["EntryTimingAction"] = "ENTER ON CONFIRMATION"
    output["EntryZoneLow"] = 10.18
    output["EntryZoneHigh"] = 10.40
    output["EntryTimingReasons"] = [
        "Price above EMA20",
        "Positive MACD histogram",
        "Breakout confirmation",
    ]
    output["EntryTimingWarnings"] = []

    output["entry_timing"] = {
        "score": 84,
        "status": "READY",
        "action": "ENTER ON CONFIRMATION",
        "entry_zone_low": 10.18,
        "entry_zone_high": 10.40,
        "reasons": [
            "Price above EMA20",
            "Positive MACD histogram",
            "Breakout confirmation",
        ],
        "warnings": [],
    }

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

    register_ai_layer_adapters(
        registry,
        regime_function=fake_apply_market_regime,
        timing_function=fake_apply_entry_timing,
        services=infrastructure.services,
    )

    received_events = []

    infrastructure.events.subscribe(
        "EntryTimingCompleted",
        lambda event: received_events.append(event),
    )

    pipeline = Pipeline(
        name="Sprint 5A.2 Entry Timing Pipeline",
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
    assert report.successful_engines == 10
    assert report.failed_engines == 0

    assert context.analysis.timing.score == 84
    assert context.analysis.timing.status == "READY"
    assert (
        context.analysis.timing.action
        == "ENTER ON CONFIRMATION"
    )
    assert context.analysis.timing.entry_zone_low == 10.18
    assert context.analysis.timing.entry_zone_high == 10.40

    assert len(context.analysis.timing.reasons) == 3
    assert context.analysis.timing.warnings == []

    assert (
        context.metadata["entry_timing_data"][
            "EntryTimingStatus"
        ]
        == "READY"
    )

    assert len(received_events) == 1

    event = received_events[0]

    assert event.name == "EntryTimingCompleted"
    assert event.payload["symbol"] == "1155.KL"
    assert event.payload["score"] == 84
    assert event.payload["status"] == "READY"
    assert (
        event.payload["action"]
        == "ENTER ON CONFIRMATION"
    )

    assert registry.names()[-1] == (
        "Entry Timing Adapter"
    )

    print("=" * 84)
    print("BURSAAI v6.0 SPRINT 5A.2 TEST")
    print("=" * 84)
    print("Entry Timing Adapter      : OK")
    print("Legacy Engine Integration : OK")
    print("Timing Score Sync         : OK")
    print("Timing Status Sync        : OK")
    print("Timing Action Sync        : OK")
    print("Entry Zone Sync           : OK")
    print("Reasons / Warnings Sync   : OK")
    print("Service Container         : OK")
    print("Event Bus Publication     : OK")
    print("Pipeline Integration      : OK")
    print("=" * 84)
    print("SPRINT 5A.2 ENTRY TIMING ADAPTER OK")


if __name__ == "__main__":
    main()
