"""BursaAI Institutional AI Brain - Version 5.3 Batch 5A."""
from statistics import pstdev
from Core.ai_conviction import calculate_conviction, normalize_engine_score, clamp, safe_float
from Core.ai_reasoning import build_reasoning


def _mapping(value, mapping, default=50):
    return mapping.get(str(value or "").upper().strip(), default)


def apply_ai_brain(result):
    if result is None:
        result = {}
    engine = result.get("_engine", {}) if isinstance(result.get("_engine", {}), dict) else {}
    trend = normalize_engine_score(engine.get("trend", {}), result.get("FinalScore", 50))
    momentum = normalize_engine_score(engine.get("momentum", {}), 50)
    volume = normalize_engine_score(engine.get("volume", {}), 40)
    smart_money = _mapping(result.get("SmartMoney"), {
        "STRONG": 95, "ACCUMULATION": 90, "CONFIRMED": 85,
        "EARLY": 70, "NEUTRAL": 50, "NONE": 35, "DISTRIBUTION": 15,
    }, 45)
    regime = _mapping(result.get("MarketRegime"), {
        "BULLISH": 90, "RECOVERY": 72, "SIDEWAYS": 48,
        "WEAK": 30, "BEARISH": 10,
    }, 45)
    mtf_data = result.get("multi_timeframe", {})
    mtf = safe_float(result.get("MTFAlignmentScore", mtf_data.get("alignment_score", 50)), 50)
    timing = safe_float(result.get("EntryTimingScore", 50), 50)
    final_score = safe_float(result.get("FinalScore", 0))
    confidence = safe_float(result.get("Confidence", 0))
    rr = safe_float(result.get("RR", 0))
    trade_quality = clamp(final_score * 0.5 + confidence * 0.35 + min(rr / 3.0, 1.0) * 100 * 0.15)

    components = {
        "trend": trend, "momentum": momentum, "volume": volume,
        "smart_money": smart_money, "market_regime": regime,
        "multi_timeframe": mtf, "entry_timing": timing,
        "trade_quality": trade_quality,
    }
    conviction = calculate_conviction(components)
    values = list(components.values())
    stability = clamp(100 - pstdev(values) if len(values) > 1 else 100)
    execution = clamp(timing * 0.50 + regime * 0.20 + trade_quality * 0.30)
    reasoning = build_reasoning(components, result, conviction)

    brain = {
        "conviction_score": conviction["score"],
        "conviction_level": conviction["level"],
        "ai_signal": conviction["signal"],
        "prediction_stability": round(stability, 2),
        "execution_quality": round(execution, 2),
        "components": {k: round(v, 2) for k, v in components.items()},
        "contributions": conviction["contributions"],
        "reasoning": reasoning,
    }
    result["ai_brain"] = brain
    result["AIConviction"] = brain["conviction_score"]
    result["AIConvictionLevel"] = brain["conviction_level"]
    result["AISignal"] = brain["ai_signal"]
    result["PredictionStability"] = brain["prediction_stability"]
    result["ExecutionQuality"] = brain["execution_quality"]
    result["AIReasoning"] = reasoning["summary"]
    return result
