"""
BursaAI v6.0 Sprint 5A.4 full integration test.

Uses injected fake functions.
No internet or live market data required.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


import pandas as pd

from Adapters.full_pipeline_registry import (
    register_full_analysis_pipeline,
)
from Framework.context import AnalysisContext
from Framework.full_pipeline import build_full_pipeline
from Framework.infrastructure import build_infrastructure


def fake_load_stock(symbol):
    return pd.DataFrame(
        {
            "Close": [10.0, 10.2, 10.4],
            "Volume": [1000, 1300, 1900],
        }
    )


def fake_add_indicators(data):
    enriched = data.copy()

    columns = {
        "EMA20": [9.9, 10.0, 10.1],
        "EMA50": [9.7, 9.8, 9.9],
        "EMA200": [9.3, 9.4, 9.5],
        "VWAP": [9.95, 10.05, 10.15],
        "ATR": [0.18, 0.20, 0.22],
        "RSI": [52, 57, 61],
        "STOCH": [55, 62, 68],
        "MACD_HISTOGRAM": [0.02, 0.04, 0.06],
        "EMA20_SLOPE": [0.01, 0.02, 0.03],
        "HIGHER_LOW": [False, True, True],
        "HIGHER_HIGH": [False, True, True],
        "BREAKOUT": [False, False, True],
        "BREAKDOWN": [False, False, False],
        "OBV": [1000, 2300, 4200],
        "OBV_MA20": [900, 1500, 2500],
    }

    for name, values in columns.items():
        enriched[name] = values

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
            "Breakout confirmation",
        ],
        "warnings": [],
    }

    return output


def fake_apply_ai_brain(result):
    output = dict(result)
    output["AIConviction"] = 86.5
    output["AIConvictionLevel"] = "INSTITUTIONAL CONVICTION"
    output["AISignal"] = "STRONG BUY"
    output["AIPredictionStability"] = 91.0
    output["AIExecutionQuality"] = 88.0
    output["AISummary"] = "Full pipeline institutional setup."
    output["AIStrengths"] = [
        "Strong trend",
        "Institutional volume",
        "Bullish regime",
    ]
    output["AIWeaknesses"] = [
        "Wait for confirmation",
    ]

    output["ai_brain"] = {
        "conviction_score": 86.5,
        "conviction_level": "INSTITUTIONAL CONVICTION",
        "ai_signal": "STRONG BUY",
        "prediction_stability": 91.0,
        "execution_quality": 88.0,
        "components": {
            "trend": 92.0,
            "momentum": 85.0,
            "volume": 88.0,
            "market_regime": 90.0,
            "entry_timing": 84.0,
        },
        "contributions": {
            "trend": 16.56,
            "momentum": 11.90,
        },
        "reasoning": {
            "strengths": [
                "Strong trend",
                "Institutional volume",
                "Bullish regime",
            ],
            "weaknesses": [
                "Wait for confirmation",
            ],
            "summary": "Full pipeline institutional setup.",
        },
    }

    return output


def main():
    infrastructure = build_infrastructure()

    bundle = build_full_pipeline(
        infrastructure,
        name="Sprint 5A.4 Full Integration Pipeline",
        failure_mode="stop",
        echo_logs=False,
        record_context_snapshot=True,
    )

    register_full_analysis_pipeline(
        bundle.registry,
        data_loader=fake_load_stock,
        indicator_function=fake_add_indicators,
        scorer=fake_calculate_score,
        trend_function=fake_score_trend,
        momentum_function=fake_score_momentum,
        volume_function=fake_score_volume,
        quality_function=fake_apply_quality_gate,
        smart_money_function=fake_apply_smart_money,
        regime_function=fake_apply_market_regime,
        timing_function=fake_apply_entry_timing,
        brain_function=fake_apply_ai_brain,
        services=infrastructure.services,
        minimum_rows=3,
    )

    context = AnalysisContext(
        symbol="1155.KL"
    )

    report = bundle.pipeline.execute(context)

    assert report.success is True
    assert report.successful_engines == 11
    assert report.failed_engines == 0
    assert report.skipped_engines == 0

    assert bundle.registry.names() == [
        "Loader Adapter",
        "Indicator Adapter",
        "Score Adapter",
        "Trend Adapter",
        "Momentum Adapter",
        "Volume Adapter",
        "Quality Gate Adapter",
        "Smart Money Adapter",
        "Market Regime Adapter",
        "Entry Timing Adapter",
        "AI Brain Adapter",
    ]

    assert context.analysis.score.final == 87
    assert context.analysis.market.regime == "BULLISH"
    assert context.analysis.timing.status == "READY"
    assert context.analysis.ai.signal == "STRONG BUY"
    assert context.analysis.ai.conviction_score == 86.5

    assert bundle.audit.count("MarketRegimeCompleted") == 1
    assert bundle.audit.count("EntryTimingCompleted") == 1
    assert bundle.audit.count("AIBrainCompleted") == 1

    assert bundle.audit.names() == [
        "MarketRegimeCompleted",
        "EntryTimingCompleted",
        "AIBrainCompleted",
    ]

    profile = bundle.profiler.summary()

    assert profile["engine_count"] == 11
    assert profile["successful"] == 11
    assert profile["failed"] == 0
    assert profile["skipped"] == 0
    assert profile["total_duration_ms"] > 0

    assert infrastructure.services.resolve(
        "engine_registry"
    ) is bundle.registry

    assert infrastructure.services.resolve(
        "pipeline"
    ) is bundle.pipeline

    assert infrastructure.services.resolve(
        "event_audit"
    ) is bundle.audit

    legacy = context.to_legacy_dict()

    assert legacy["Code"] == "1155.KL"
    assert legacy["FinalScore"] == 87
    assert legacy["EntryTimingStatus"] == "READY"
    assert legacy["AISignal"] == "STRONG BUY"

    print("=" * 88)
    print("BURSAAI v6.0 SPRINT 5A.4 FULL INTEGRATION TEST")
    print("=" * 88)
    print("Full Adapter Registry       : OK")
    print("Complete Pipeline Ordering  : OK")
    print("11 Engine Execution         : OK")
    print("Dependency Validation       : OK")
    print("Analysis Context Sync       : OK")
    print("Market Regime Event         : OK")
    print("Entry Timing Event          : OK")
    print("AI Brain Event              : OK")
    print("Event Audit Trail           : OK")
    print("Profiler Integration        : OK")
    print("Service Container Binding   : OK")
    print("Legacy Output Bridge        : OK")
    print("Execution Report            : OK")
    print("=" * 88)
    print("SPRINT 5A.4 AI LAYER FULL INTEGRATION OK")


if __name__ == "__main__":
    main()
