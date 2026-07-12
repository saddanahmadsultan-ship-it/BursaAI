"""
=========================================
BursaAI Institutional Smart Money Engine
Version : 4.3.1 Strict Stable
=========================================
"""


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def _has_column(data, column):
    return column in data.columns


def apply_smart_money_engine(data, result):
    bonus = 0
    reasons = []
    strong_flags = 0

    if data is None or data.empty:
        result["InstitutionBonus"] = 0
        result["FinalScore"] = result.get("TradeableScore", result.get("Score", 0))
        result["SmartMoney"] = "NONE"
        return result

    last = data.iloc[-1]

    close = _safe_float(last.get("Close", 0))
    volume = _safe_float(last.get("Volume", 0))

    tradeable_score = int(result.get("TradeableScore", result.get("Score", 0)))
    confidence = _safe_float(result.get("Confidence", 0))
    trend = str(result.get("Trend", "")).upper()
    volume_strength = str(result.get("Volume", "")).upper()

    avg20_volume = 0
    volume_ratio = 0

    if _has_column(data, "Volume"):
        avg20_volume = _safe_float(data["Volume"].rolling(20).mean().iloc[-1])

        if avg20_volume > 0:
            volume_ratio = volume / avg20_volume

    # ==========================
    # VOLUME
    # ==========================

    if volume_ratio >= 2.0:
        bonus += 8
        strong_flags += 1
        reasons.append("Institutional Volume Expansion")

    elif volume_ratio >= 1.5:
        bonus += 6
        strong_flags += 1
        reasons.append("Strong Volume Expansion")

    elif volume_ratio >= 1.2:
        bonus += 3
        reasons.append("Above Average Volume")

    elif volume_ratio > 0 and volume_ratio < 0.7 and trend in ["UPTREND", "WEAK UPTREND"]:
        bonus += 2
        reasons.append("Volume Dry Up Setup")

    # ==========================
    # OBV
    # ==========================

    if _has_column(data, "OBV") and _has_column(data, "OBV_MA20"):
        obv = _safe_float(last.get("OBV", 0))
        obv_ma20 = _safe_float(last.get("OBV_MA20", 0))

        if obv > obv_ma20:
            bonus += 3
            reasons.append("OBV Above MA20")

        if len(data) >= 5:
            obv_prev = _safe_float(data["OBV"].iloc[-5])

            if obv > obv_prev:
                bonus += 2
                reasons.append("OBV Rising")

    # ==========================
    # CMF
    # ==========================

    if _has_column(data, "CMF"):
        cmf = _safe_float(last.get("CMF", 0))

        if cmf >= 0.20:
            bonus += 6
            strong_flags += 1
            reasons.append("Strong Positive CMF")

        elif cmf >= 0.10:
            bonus += 4
            reasons.append("Positive CMF")

        elif cmf > 0:
            bonus += 1
            reasons.append("Mild Positive CMF")

        elif cmf <= -0.10:
            bonus -= 4
            reasons.append("Negative CMF Penalty")

    # ==========================
    # VWAP
    # ==========================

    if _has_column(data, "VWAP"):
        vwap = _safe_float(last.get("VWAP", 0))

        if vwap > 0 and close > vwap:
            bonus += 3
            reasons.append("Price Above VWAP")

        elif vwap > 0 and close < vwap:
            bonus -= 2
            reasons.append("Below VWAP Penalty")

    # ==========================
    # STRUCTURE
    # ==========================

    higher_low = bool(last.get("HIGHER_LOW", False))
    higher_high = bool(last.get("HIGHER_HIGH", False))
    breakout = bool(last.get("BREAKOUT", False))

    if higher_low:
        bonus += 2
        reasons.append("Higher Low")

    if higher_high:
        bonus += 2
        reasons.append("Higher High")

    if breakout and volume_ratio >= 1.2:
        bonus += 5
        strong_flags += 1
        reasons.append("Breakout With Volume")

    # ==========================
    # MOMENTUM
    # ==========================

    if _has_column(data, "MACD") and _has_column(data, "MACD_SIGNAL"):
        macd = _safe_float(last.get("MACD", 0))
        macd_signal = _safe_float(last.get("MACD_SIGNAL", 0))

        if macd > macd_signal:
            bonus += 2
            reasons.append("MACD Bullish")

    if _has_column(data, "ROC"):
        roc = _safe_float(last.get("ROC", 0))

        if roc > 0:
            bonus += 1
            reasons.append("Positive ROC")

    # ==========================
    # ATR
    # ==========================

    if _has_column(data, "ATR_PERCENT"):
        atr_percent = _safe_float(last.get("ATR_PERCENT", 0))

        if 1.0 <= atr_percent <= 3.5:
            bonus += 2
            reasons.append("Healthy ATR")

        elif atr_percent > 5:
            bonus -= 5
            reasons.append("High Volatility Penalty")

    # ==========================
    # CAPS
    # ==========================

    if volume_strength == "WEAK":
        bonus = min(bonus, 8)

    if trend == "SIDEWAYS":
        bonus = min(bonus, 6)

    if trend == "DOWNTREND":
        bonus = min(bonus, 2)

    if confidence < 40:
        bonus = min(bonus, 2)

    bonus = max(0, bonus)

    final_score = max(0, min(100, tradeable_score + bonus))

    # ==========================
    # SMART MONEY LABEL
    # ==========================

    if (
        bonus >= 10
        and strong_flags >= 2
        and volume_strength != "WEAK"
        and trend == "UPTREND"
        and confidence >= 65
    ):
        smart_money = "STRONG"

    elif bonus >= 7 and strong_flags >= 1 and trend in ["UPTREND", "WEAK UPTREND"]:
        smart_money = "MODERATE"

    elif bonus >= 3:
        smart_money = "EARLY"

    else:
        smart_money = "NONE"

    # ==========================
    # GRADE
    # ==========================

    if final_score >= 80:
        final_grade = "A"
    elif final_score >= 70:
        final_grade = "B+"
    elif final_score >= 60:
        final_grade = "B"
    elif final_score >= 50:
        final_grade = "C"
    elif final_score >= 35:
        final_grade = "D"
    else:
        final_grade = "F"

    # ==========================
    # SIGNAL
    # ==========================

    if final_score >= 75 and confidence >= 65 and trend == "UPTREND" and volume_strength != "WEAK":
        final_signal = "BUY"

    elif final_score >= 62 and confidence >= 60 and trend in ["UPTREND", "WEAK UPTREND"]:
        final_signal = "WATCH"

    elif final_score >= 50 and confidence >= 50 and trend != "DOWNTREND":
        final_signal = "HOLD"

    else:
        final_signal = "AVOID"

    result["InstitutionBonus"] = bonus
    result["FinalScore"] = final_score
    result["Score"] = final_score
    result["Grade"] = final_grade
    result["Signal"] = final_signal
    result["SmartMoney"] = smart_money

    if "Reason" not in result or result["Reason"] is None:
        result["Reason"] = []

    result["Reason"] = result["Reason"] + reasons

    return result