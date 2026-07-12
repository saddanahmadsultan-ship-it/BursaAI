"""
=========================================
BursaAI Market Regime Engine
Version : 4.4 Stable
=========================================
"""


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def apply_market_regime_engine(data, result):
    regime_score = 0
    regime_penalty = 0
    regime_bonus = 0
    reasons = []

    if data is None or data.empty:
        result["MarketRegime"] = "UNKNOWN"
        result["RegimeScore"] = 0
        result["RegimePenalty"] = 0
        result["FinalScore"] = result.get("FinalScore", result.get("Score", 0))
        return result

    last = data.iloc[-1]

    close = _safe_float(last.get("Close", 0))
    ema20 = _safe_float(last.get("EMA20", 0))
    ema50 = _safe_float(last.get("EMA50", 0))
    ema200 = _safe_float(last.get("EMA200", 0))
    ema20_slope = _safe_float(last.get("EMA20_SLOPE", 0))
    atr_percent = _safe_float(last.get("ATR_PERCENT", 0))
    rsi = _safe_float(last.get("RSI", 0))
    macd = _safe_float(last.get("MACD", 0))
    macd_signal = _safe_float(last.get("MACD_SIGNAL", 0))

    final_score = int(result.get("FinalScore", result.get("Score", 0)))
    confidence = _safe_float(result.get("Confidence", 0))
    trend = str(result.get("Trend", "")).upper()
    volume = str(result.get("Volume", "")).upper()

    # ==========================
    # EMA MARKET STRUCTURE
    # ==========================

    if close > ema20:
        regime_score += 8
        reasons.append("Regime: Price above EMA20")
    else:
        regime_score -= 6
        reasons.append("Regime: Price below EMA20")

    if close > ema50:
        regime_score += 8
        reasons.append("Regime: Price above EMA50")
    else:
        regime_score -= 6
        reasons.append("Regime: Price below EMA50")

    if close > ema200:
        regime_score += 10
        reasons.append("Regime: Price above EMA200")
    else:
        regime_score -= 10
        reasons.append("Regime: Price below EMA200")

    if ema20 > ema50 > ema200:
        regime_score += 15
        reasons.append("Regime: Bullish EMA Alignment")

    elif ema20 < ema50 < ema200:
        regime_score -= 15
        reasons.append("Regime: Bearish EMA Alignment")

    if ema20_slope > 0:
        regime_score += 6
        reasons.append("Regime: EMA20 rising")
    else:
        regime_score -= 5
        reasons.append("Regime: EMA20 falling")

    # ==========================
    # MOMENTUM REGIME
    # ==========================

    if rsi >= 55:
        regime_score += 6
        reasons.append("Regime: RSI bullish")
    elif rsi >= 45:
        regime_score += 2
        reasons.append("Regime: RSI neutral")
    else:
        regime_score -= 6
        reasons.append("Regime: RSI weak")

    if macd > macd_signal:
        regime_score += 5
        reasons.append("Regime: MACD bullish")
    else:
        regime_score -= 5
        reasons.append("Regime: MACD bearish")

    # ==========================
    # VOLATILITY REGIME
    # ==========================

    if atr_percent <= 0:
        regime_score += 0

    elif atr_percent < 1.0:
        regime_score -= 3
        reasons.append("Regime: Very low volatility")

    elif 1.0 <= atr_percent <= 3.5:
        regime_score += 5
        reasons.append("Regime: Healthy volatility")

    elif 3.5 < atr_percent <= 5.0:
        regime_score -= 4
        reasons.append("Regime: High volatility")

    else:
        regime_score -= 10
        reasons.append("Regime: Extreme volatility")

    # ==========================
    # REGIME CLASSIFICATION
    # ==========================

    if regime_score >= 40:
        market_regime = "BULLISH"
        regime_bonus = 5

    elif regime_score >= 20:
        market_regime = "RECOVERY"
        regime_bonus = 2

    elif regime_score >= 5:
        market_regime = "SIDEWAYS"
        regime_penalty = 4

    elif regime_score >= -15:
        market_regime = "WEAK"
        regime_penalty = 8

    else:
        market_regime = "BEARISH"
        regime_penalty = 15

    # ==========================
    # EXTRA SAFETY FILTER
    # ==========================

    if trend == "DOWNTREND":
        regime_penalty += 8
        reasons.append("Regime: Dowtrend extra penalty")

    if volume == "WEAK" and market_regime in ["WEAK", "BEARISH"]:
        regime_penalty += 5
        reasons.append("Regime: Weak volume in weak market")

    if confidence < 40 and market_regime in ["WEAK", "BEARISH"]:
        regime_penalty += 5
        reasons.append("Regime: Low confidence in weak market")

    adjusted_score = final_score + regime_bonus - regime_penalty
    adjusted_score = max(0, min(100, adjusted_score))

    # ==========================
    # FINAL GRADE
    # ==========================

    if adjusted_score >= 80:
        final_grade = "A"
    elif adjusted_score >= 70:
        final_grade = "B+"
    elif adjusted_score >= 60:
        final_grade = "B"
    elif adjusted_score >= 50:
        final_grade = "C"
    elif adjusted_score >= 35:
        final_grade = "D"
    else:
        final_grade = "F"

    # ==========================
    # FINAL SIGNAL
    # ==========================

    if (
        adjusted_score >= 75
        and confidence >= 65
        and market_regime == "BULLISH"
        and trend == "UPTREND"
        and volume != "WEAK"
    ):
        final_signal = "BUY"

    elif (
        adjusted_score >= 62
        and confidence >= 60
        and market_regime in ["BULLISH", "RECOVERY"]
        and trend in ["UPTREND", "WEAK UPTREND"]
    ):
        final_signal = "WATCH"

    elif (
        adjusted_score >= 50
        and confidence >= 50
        and market_regime not in ["BEARISH"]
        and trend != "DOWNTREND"
    ):
        final_signal = "HOLD"

    else:
        final_signal = "AVOID"

    result["MarketRegime"] = market_regime
    result["RegimeScore"] = regime_score
    result["RegimeBonus"] = regime_bonus
    result["RegimePenalty"] = regime_penalty
    result["FinalScore"] = adjusted_score
    result["Score"] = adjusted_score
    result["Grade"] = final_grade
    result["Signal"] = final_signal

    if "Reason" not in result or result["Reason"] is None:
        result["Reason"] = []

    result["Reason"] = result["Reason"] + reasons

    return result