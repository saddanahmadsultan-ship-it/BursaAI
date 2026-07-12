"""
=========================================
BursaAI Quality Gate Engine
Version : 4.2.2 Balanced Stable
=========================================
"""


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def _safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def apply_quality_gate(result):
    raw_score = _safe_int(result.get("Score", 0))
    confidence = _safe_float(result.get("Confidence", 0))
    trend = str(result.get("Trend", "")).upper()
    volume = str(result.get("Volume", "")).upper()
    rating = str(result.get("Rating", "")).upper()
    rr = _safe_float(result.get("RR", 0))
    warning = result.get("Warning", [])

    if warning is None:
        warning = []

    penalty = 0
    gate_reason = []

    # ==========================
    # VOLUME FILTER
    # ==========================

    if volume == "WEAK":
        penalty += 7
        gate_reason.append("Quality Gate: Weak Volume")
    elif volume == "VERY WEAK":
        penalty += 10
        gate_reason.append("Quality Gate: Very Weak Volume")

    # ==========================
    # CONFIDENCE FILTER
    # ==========================

    if confidence < 30:
        penalty += 14
        gate_reason.append("Quality Gate: Extremely Low Confidence")
    elif confidence < 40:
        penalty += 10
        gate_reason.append("Quality Gate: Very Low Confidence")
    elif confidence < 55:
        penalty += 5
        gate_reason.append("Quality Gate: Low Confidence")

    # ==========================
    # TREND FILTER
    # ==========================

    if trend == "DOWNTREND":
        penalty += 15
        gate_reason.append("Quality Gate: Dowtrend")
    elif trend == "SIDEWAYS":
        penalty += 9
        gate_reason.append("Quality Gate: Sideways Market")
    elif trend == "WEAK UPTREND":
        penalty += 4
        gate_reason.append("Quality Gate: Weak Uptrend")

    # ==========================
    # AI RATING FILTER
    # ==========================

    if rating == "D":
        penalty += 5
        gate_reason.append("Quality Gate: Weak AI Rating")
    elif rating == "C":
        penalty += 2
        gate_reason.append("Quality Gate: Moderate AI Rating")

    # ==========================
    # RISK REWARD FILTER
    # ==========================

    if rr < 1.5:
        penalty += 8
        gate_reason.append("Quality Gate: Poor Risk Reward")
    elif rr < 2.0:
        penalty += 3
        gate_reason.append("Quality Gate: Moderate Risk Reward")

    # ==========================
    # TRADEABLE SCORE
    # ==========================

    tradeable_score = max(0, raw_score - penalty)

    # ==========================
    # FINAL SIGNAL
    # ==========================

    if (
        tradeable_score >= 80
        and confidence >= 70
        and trend == "UPTREND"
        and volume != "WEAK"
    ):
        final_signal = "BUY"

    elif (
        tradeable_score >= 65
        and confidence >= 60
        and trend in ["UPTREND", "WEAK UPTREND"]
    ):
        final_signal = "WATCH"

    elif (
        tradeable_score >= 50
        and confidence >= 50
        and trend != "DOWNTREND"
    ):
        final_signal = "HOLD"

    else:
        final_signal = "AVOID"

    # ==========================
    # FINAL GRADE
    # ==========================

    if tradeable_score >= 80:
        final_grade = "A"
    elif tradeable_score >= 70:
        final_grade = "B+"
    elif tradeable_score >= 60:
        final_grade = "B"
    elif tradeable_score >= 50:
        final_grade = "C"
    elif tradeable_score >= 35:
        final_grade = "D"
    else:
        final_grade = "F"

    result["RawScore"] = raw_score
    result["QualityPenalty"] = penalty
    result["TradeableScore"] = tradeable_score
    result["Score"] = tradeable_score
    result["Grade"] = final_grade
    result["Signal"] = final_signal
    result["Warning"] = warning + gate_reason

    return result