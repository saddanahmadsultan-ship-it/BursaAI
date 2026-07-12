"""
=========================================================
BursaAI Dynamic Risk Manager
Version : 5.2 Batch 4B
=========================================================
"""

from Core.portfolio_config import get_portfolio_config
from Core.entry_timing_config import TIMING_RISK_MULTIPLIER
from Core.ai_weights import AI_RISK_MULTIPLIER
from Core.dynamic_risk_config import (
    MIN_DYNAMIC_RISK_PERCENT,
    MAX_DYNAMIC_RISK_PERCENT,
    REGIME_MULTIPLIER,
    VOLATILITY_MULTIPLIER,
    CONFIDENCE_BANDS,
    SCORE_BANDS,
    RR_BANDS,
    SMART_MONEY_MULTIPLIER,
)


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _band_multiplier(value, bands):
    number = _safe_float(value)
    for minimum, multiplier in bands:
        if number >= minimum:
            return float(multiplier)
    return 0.0


def _normalise(value, default="UNKNOWN"):
    text = str(value or default).upper().strip()
    return text if text else default


def _volatility_label(result):
    engine = result.get("_engine", {})
    volatility = engine.get("volatility", {}) if isinstance(engine, dict) else {}

    for key in ("level", "strength", "status", "quality", "regime"):
        value = volatility.get(key) if isinstance(volatility, dict) else None
        if value:
            return _normalise(value)

    atr_percent = _safe_float(result.get("ATRPercent", 0))
    if atr_percent <= 0:
        return "UNKNOWN"
    if atr_percent <= 2.0:
        return "LOW"
    if atr_percent <= 4.0:
        return "NORMAL"
    if atr_percent <= 6.0:
        return "HIGH"
    return "EXTREME"


def apply_dynamic_risk_manager(result):
    """Calculate the final risk percentage before position sizing."""

    if result is None:
        result = {}

    config = get_portfolio_config()
    base_risk = _safe_float(config.get("risk_percent", 0))
    signal_map = config.get("signal_risk_multiplier", {})

    signal = _normalise(result.get("Signal"))
    timing = _normalise(
        result.get(
            "EntryTimingStatus",
            result.get("entry_timing", {}).get("status", "UNKNOWN")
        )
    )
    regime = _normalise(result.get("MarketRegime"))
    volatility = _volatility_label(result)
    smart_money = _normalise(result.get("SmartMoney", "NONE"), "NONE")
    ai_level = _normalise(result.get("AIConvictionLevel", "MODERATE CONVICTION"))

    confidence = _safe_float(result.get("Confidence", 0))
    final_score = _safe_float(result.get("FinalScore", 0))
    rr = _safe_float(result.get("RR", 0))

    signal_multiplier = _safe_float(
        signal_map.get(signal, signal_map.get("UNKNOWN", 0))
    )
    timing_multiplier = _safe_float(
        TIMING_RISK_MULTIPLIER.get(timing, TIMING_RISK_MULTIPLIER.get("UNKNOWN", 0))
    )
    regime_multiplier = _safe_float(
        REGIME_MULTIPLIER.get(regime, REGIME_MULTIPLIER["UNKNOWN"])
    )
    volatility_multiplier = _safe_float(
        VOLATILITY_MULTIPLIER.get(volatility, VOLATILITY_MULTIPLIER["UNKNOWN"])
    )
    confidence_multiplier = _band_multiplier(confidence, CONFIDENCE_BANDS)
    score_multiplier = _band_multiplier(final_score, SCORE_BANDS)
    rr_multiplier = _band_multiplier(rr, RR_BANDS)
    smart_money_multiplier = _safe_float(
        SMART_MONEY_MULTIPLIER.get(
            smart_money,
            SMART_MONEY_MULTIPLIER["UNKNOWN"]
        )
    )
    ai_conviction_multiplier = _safe_float(
        AI_RISK_MULTIPLIER.get(ai_level, 0.85)
    )

    multipliers = {
        "signal": signal_multiplier,
        "timing": timing_multiplier,
        "regime": regime_multiplier,
        "volatility": volatility_multiplier,
        "confidence": confidence_multiplier,
        "score": score_multiplier,
        "risk_reward": rr_multiplier,
        "smart_money": smart_money_multiplier,
        "ai_conviction": ai_conviction_multiplier,
    }

    blocked_reasons = []
    if signal_multiplier <= 0:
        blocked_reasons.append("SIGNAL BLOCKED")
    if timing_multiplier <= 0:
        blocked_reasons.append("TIMING BLOCKED")
    if regime_multiplier <= 0:
        blocked_reasons.append("BEARISH REGIME")
    if confidence_multiplier <= 0:
        blocked_reasons.append("LOW CONFIDENCE")
    if score_multiplier <= 0:
        blocked_reasons.append("LOW SCORE")
    if rr_multiplier <= 0:
        blocked_reasons.append("POOR RISK REWARD")
    if ai_conviction_multiplier <= 0:
        blocked_reasons.append("NO AI CONVICTION")

    combined_multiplier = 1.0
    for multiplier in multipliers.values():
        combined_multiplier *= multiplier

    calculated_risk = base_risk * combined_multiplier

    if blocked_reasons or calculated_risk <= 0:
        final_risk = 0.0
        status = "BLOCKED"
        reason = ", ".join(blocked_reasons) or "DYNAMIC RISK ZERO"
    else:
        final_risk = max(
            MIN_DYNAMIC_RISK_PERCENT,
            min(calculated_risk, MAX_DYNAMIC_RISK_PERCENT)
        )

        if final_risk >= 0.70:
            status = "NORMAL RISK"
        elif final_risk >= 0.35:
            status = "REDUCED RISK"
        else:
            status = "MINIMUM RISK"

        reason = "RISK ADJUSTED BY MARKET AND TRADE QUALITY"

    dynamic = {
        "base_risk_percent": round(base_risk, 4),
        "combined_multiplier": round(combined_multiplier, 6),
        "calculated_risk_percent": round(calculated_risk, 4),
        "final_risk_percent": round(final_risk, 4),
        "status": status,
        "reason": reason,
        "volatility": volatility,
        "multipliers": {key: round(value, 4) for key, value in multipliers.items()},
    }

    result["dynamic_risk"] = dynamic
    result["BaseRiskPercent"] = dynamic["base_risk_percent"]
    result["DynamicRiskMultiplier"] = dynamic["combined_multiplier"]
    result["CalculatedRiskPercent"] = dynamic["calculated_risk_percent"]
    result["DynamicRiskPercent"] = dynamic["final_risk_percent"]
    result["DynamicRiskStatus"] = dynamic["status"]
    result["DynamicRiskReason"] = dynamic["reason"]
    result["DynamicVolatility"] = dynamic["volatility"]

    result["SignalRiskMultiplier"] = multipliers["signal"]
    result["TimingRiskMultiplier"] = multipliers["timing"]
    result["RegimeRiskMultiplier"] = multipliers["regime"]
    result["VolatilityRiskMultiplier"] = multipliers["volatility"]
    result["ConfidenceRiskMultiplier"] = multipliers["confidence"]
    result["ScoreRiskMultiplier"] = multipliers["score"]
    result["RRRiskMultiplier"] = multipliers["risk_reward"]
    result["SmartMoneyRiskMultiplier"] = multipliers["smart_money"]
    result["AIConvictionRiskMultiplier"] = multipliers["ai_conviction"]

    return result
