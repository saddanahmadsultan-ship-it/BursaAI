"""
BursaAI v6.0 Sprint 5B full execution-layer test.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

from Adapters.full_pipeline_registry import register_full_analysis_pipeline
from Framework.context import AnalysisContext
from Framework.full_pipeline import build_full_pipeline
from Framework.infrastructure import build_infrastructure


def fake_load_stock(symbol):
    return pd.DataFrame({
        "Close": [10.0, 10.2, 10.4],
        "MA20": [9.8, 9.9, 10.0],
        "MA50": [9.5, 9.6, 9.7],
        "MA200": [9.0, 9.1, 9.2],
        "EMA20": [9.8, 9.9, 10.0],
        "EMA50": [9.5, 9.6, 9.7],
        "EMA200": [9.0, 9.1, 9.2],
        "EMA20_SLOPE": [0.01, 0.02, 0.03],
        "ATR": [0.2, 0.2, 0.2],
        "ATR_PERCENT": [1.9, 1.9, 1.9],
        "RSI": [55, 60, 65],
        "STOCH": [50, 60, 70],
        "CCI": [50, 90, 120],
        "ROC": [2, 4, 6],
        "MACD": [0.1, 0.2, 0.3],
        "MACD_SIGNAL": [0.05, 0.1, 0.2],
        "MACD_HISTOGRAM": [0.05, 0.1, 0.1],
        "VWAP": [9.9, 10.0, 10.1],
        "HIGHER_HIGH": [False, True, True],
        "HIGHER_LOW": [False, True, True],
        "LOWER_HIGH": [False, False, False],
        "BREAKOUT": [False, False, True],
        "BREAKDOWN": [False, False, False],
        "OBV": [1000, 2000, 3000],
        "OBV_MA20": [900, 1500, 2500],
        "Volume": [1000, 1300, 1900],
    })


def fake_add_indicators(data):
    return data.copy()


def fake_calculate_score(data):
    return {
        "score": 82,
        "grade": "A",
        "trend": {"score": 24, "direction": "STRONG UPTREND"},
        "momentum": {"score": 21, "quality": "STRONG"},
        "volume": {"score": 15, "strength": "STRONG"},
        "volatility": {"score": 10, "level": "STABLE"},
        "risk": {"score": 13, "rr": 2.5},
    }


def fake_score_trend(data):
    return {"score": 24, "direction": "STRONG UPTREND"}


def fake_score_momentum(data):
    return {"score": 21, "quality": "STRONG"}


def fake_score_volume(data):
    return {"score": 15, "strength": "STRONG"}


def fake_quality(result):
    output = dict(result)
    output["QualityPenalty"] = 5
    output["TradeableScore"] = 77
    output["FinalScore"] = 77
    output.setdefault("score", {}).update({
        "quality_penalty": 5,
        "tradeable": 77,
        "final": 77,
    })
    return output


def fake_smart_money(data, result):
    output = dict(result)
    output["InstitutionBonus"] = 8
    output["SmartMoney"] = "EARLY"
    output["FinalScore"] = 85
    output.setdefault("score", {}).update({
        "institution_bonus": 8,
        "final": 85,
    })
    output.setdefault("market", {})["smart_money"] = "EARLY"
    return output


def fake_regime(data, result):
    output = dict(result)
    output["MarketRegime"] = "BULLISH"
    output["RegimeScore"] = 60
    output["RegimeBonus"] = 3
    output["FinalScore"] = 88
    output.setdefault("market", {}).update({
        "regime": "BULLISH",
        "regime_score": 60,
    })
    output.setdefault("score", {}).update({
        "regime_bonus": 3,
        "final": 88,
    })
    return output


def fake_timing(data, result):
    output = dict(result)
    output["EntryTimingScore"] = 85
    output["EntryTimingStatus"] = "READY"
    output["EntryTimingAction"] = "ENTER ON CONFIRMATION"
    output["entry_timing"] = {
        "score": 85,
        "status": "READY",
        "action": "ENTER ON CONFIRMATION",
        "entry_zone_low": 10.2,
        "entry_zone_high": 10.4,
        "reasons": ["Breakout confirmation"],
        "warnings": [],
    }
    return output


def fake_brain(result):
    output = dict(result)
    output["AIConviction"] = 87
    output["AIConvictionLevel"] = "INSTITUTIONAL CONVICTION"
    output["AISignal"] = "STRONG BUY"
    output["ai_brain"] = {
        "conviction_score": 87,
        "conviction_level": "INSTITUTIONAL CONVICTION",
        "ai_signal": "STRONG BUY",
        "prediction_stability": 90,
        "execution_quality": 88,
        "components": {},
        "contributions": {},
        "reasoning": {
            "strengths": ["Strong setup"],
            "weaknesses": [],
            "summary": "Strong setup",
        },
    }
    return output


def fake_confidence(trend, momentum, volume, volatility, risk, modifier):
    return {
        "confidence": 92,
        "level": "VERY HIGH",
        "reason": ["Strong Trend", "Positive AI Modifier"],
    }


def fake_strategy(data, score, trend, momentum, volume, confidence):
    return {
        "strategy": "STRONG BUY",
        "entry": 10.4,
        "stoploss": 10.0,
        "target": 11.2,
        "rr": 2.0,
        "bullish": True,
        "warning": [],
    }


def fake_decision(result):
    return {
        "analysis": ["Institutional Trend", "Very High Confidence"],
        "warnings": [],
        "quality": 82.0,
        "rating": "A+",
        "recommendation": "BUY",
        "summary": "Quality 82.0/100 | Score 88 | Confidence 92.0% | RR 2.00",
    }


def main():
    infrastructure = build_infrastructure()
    bundle = build_full_pipeline(
        infrastructure,
        name="Sprint 5B Full Pipeline",
        failure_mode="stop",
        echo_logs=False,
    )

    register_full_analysis_pipeline(
        bundle.registry,
        data_loader=fake_load_stock,
        indicator_function=fake_add_indicators,
        scorer=fake_calculate_score,
        trend_function=fake_score_trend,
        momentum_function=fake_score_momentum,
        volume_function=fake_score_volume,
        quality_function=fake_quality,
        smart_money_function=fake_smart_money,
        regime_function=fake_regime,
        timing_function=fake_timing,
        brain_function=fake_brain,
        confidence_function=fake_confidence,
        strategy_function=fake_strategy,
        decision_function=fake_decision,
        services=infrastructure.services,
        minimum_rows=3,
    )

    context = AnalysisContext(symbol="1155.KL")
    report = bundle.pipeline.execute(context)

    assert report.success is True
    assert report.successful_engines == 14
    assert context.analysis.confidence == 92
    assert context.analysis.confidence_level == "VERY HIGH"
    assert context.analysis.trade.signal == "STRONG BUY"
    assert context.analysis.trade.entry == 10.4
    assert context.analysis.trade.risk_reward == 2.0
    assert context.analysis.trade.decision_signal == "BUY"
    assert context.analysis.trade.rating == "A+"
    assert context.analysis.extra["decision_quality"] == 82.0
    assert bundle.audit.count("ConfidenceCalculated") == 1
    assert bundle.audit.count("StrategyGenerated") == 1
    assert bundle.audit.count("DecisionCompleted") == 1

    print("=" * 84)
    print("BURSAAI v6.0 SPRINT 5B TEST")
    print("=" * 84)
    print("Confidence Adapter       : OK")
    print("Strategy Adapter         : OK")
    print("Decision Adapter         : OK")
    print("Execution Registry       : OK")
    print("14 Engine Pipeline       : OK")
    print("Confidence Event         : OK")
    print("Strategy Event           : OK")
    print("Decision Event           : OK")
    print("Context Synchronization  : OK")
    print("=" * 84)
    print("SPRINT 5B EXECUTION LAYER OK")


if __name__ == "__main__":
    main()
