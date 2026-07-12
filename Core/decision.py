"""
=========================================
BursaAI Decision Engine
Version : 6.1 Institutional
Backward Compatible
=========================================
"""


def make_decision(result):

    analysis = []
    warnings = []

    # =====================================
    # PRICE
    # =====================================

    price = result.get("price", 0)

    ema20 = result.get("ema20", 0)
    ema50 = result.get("ema50", 0)
    ema200 = result.get("ema200", 0)

    ema20_slope = result.get("ema20_slope", 0)

    # =====================================
    # EMA TREND
    # =====================================

    if ema20 > ema50:
        analysis.append("EMA20 above EMA50")
    else:
        warnings.append("EMA20 below EMA50")

    if ema50 > ema200:
        analysis.append("EMA50 above EMA200")
    else:
        warnings.append("EMA50 below EMA200")

    if price > ema20:
        analysis.append("Price above EMA20")

    if ema20_slope > 0:
        analysis.append("EMA20 Rising")

    # =====================================
    # MARKET STRUCTURE
    # =====================================

    if result.get("higher_high", False):
        analysis.append("Higher High")

    if result.get("higher_low", False):
        analysis.append("Higher Low")

    if result.get("lower_high", False):
        warnings.append("Lower High")

    if result.get("breakout", False):
        analysis.append("20-Day Breakout")

    if result.get("breakdown", False):
        warnings.append("20-Day Breakdown")

    # =====================================
    # VWAP
    # =====================================

    vwap = result.get("vwap", 0)

    if price > vwap:
        analysis.append("Above VWAP")
    else:
        warnings.append("Below VWAP")

    # =====================================
    # RSI
    # =====================================

    rsi = result.get("rsi", 50)

    if 55 <= rsi <= 70:
        analysis.append("Healthy RSI")

    elif 45 <= rsi < 55:
        analysis.append("Recovering RSI")

    elif rsi > 70:
        warnings.append("Overbought RSI")

    elif rsi < 30:
        warnings.append("Oversold RSI")

    # =====================================
    # STOCHASTIC
    # =====================================

    stoch = result.get("stoch", 50)

    if stoch > 80:
        warnings.append("Stochastic Overbought")

    elif stoch < 20:
        analysis.append("Stochastic Reversal")

    # =====================================
    # CCI
    # =====================================

    cci = result.get("cci", 0)

    if cci > 100:
        analysis.append("Strong CCI")

    elif cci < -100:
        warnings.append("Weak CCI")

    # =====================================
    # ROC
    # =====================================

    roc = result.get("roc", 0)

    if roc > 5:
        analysis.append("Strong Momentum")

    elif roc > 0:
        analysis.append("Positive Momentum")

    else:
        warnings.append("Negative Momentum")

    # =====================================
    # MACD
    # =====================================

    if result.get("macd_signal") == "Bullish":
        analysis.append("MACD Bullish")
    else:
        warnings.append("MACD Bearish")

    if result.get("macd", 0) > 0:
        analysis.append("MACD Above Zero")

    if result.get("macd_histogram", 0) > 0:
        analysis.append("Positive Histogram")
    else:
        warnings.append("Negative Histogram")

    # =====================================
    # VOLUME
    # =====================================

    volume = result.get("volume_score", 0)

    if volume >= 12:
        analysis.append("Institutional Volume")

    elif volume >= 8:
        analysis.append("Strong Volume")

    elif volume >= 5:
        analysis.append("Average Volume")

    else:
        warnings.append("Weak Volume")

    if result.get("obv_bullish", False):
        analysis.append("OBV Bullish")

    # =====================================
    # ATR
    # =====================================

    atr = result.get("atr_percent", 0)

    if atr < 2:
        analysis.append("Stable Volatility")

    elif atr < 5:
        analysis.append("Healthy Volatility")

    else:
        warnings.append("High Volatility")

    # =====================================
    # CONFIDENCE
    # =====================================

    confidence = result.get("confidence", 0)

    if confidence >= 80:
        analysis.append("Very High Confidence")

    elif confidence >= 65:
        analysis.append("High Confidence")

    elif confidence < 40:
        warnings.append("Low Confidence")

    # =====================================
    # RISK REWARD
    # =====================================

    rr = result.get("rr", 0)

    if rr >= 2:
        analysis.append(f"Good Risk Reward ({rr:.2f})")
    else:
        warnings.append("Poor Risk Reward")

    # =====================================
    # TREND
    # =====================================

    trend = result.get("trend", "")

    if trend == "STRONG UPTREND":
        analysis.append("Institutional Trend")

    elif trend == "UPTREND":
        analysis.append("Uptrend")

    elif trend == "WEAK UPTREND":
        warnings.append("Weak Uptrend")

    elif trend == "SIDEWAYS":
        warnings.append("Sideways Market")

    elif trend == "DOWNTREND":
        warnings.append("Downtrend")

    # =====================================
    # QUALITY SCORE
    # =====================================

    quality = (
        len(analysis) * 4
        -
        len(warnings) * 3
    )

    quality = max(0, min(100, quality))

    # =====================================
    # RATING
    # =====================================

    if quality >= 70:
        rating = "A+"

    elif quality >= 60:
        rating = "A"

    elif quality >= 50:
        rating = "B+"

    elif quality >= 40:
        rating = "B"

    elif quality >= 30:
        rating = "C"

    else:
        rating = "D"

    # =====================================
    # RECOMMENDATION
    # =====================================

    if (
        quality >= 60
        and confidence >= 75
        and rr >= 2
    ):

        recommendation = "BUY"

    elif (
        quality >= 45
        and confidence >= 60
    ):

        recommendation = "WATCH"

    elif (
        quality >= 30
    ):

        recommendation = "HOLD"

    else:

        recommendation = "AVOID"

    # =====================================
    # SUMMARY
    # =====================================

    summary = (
        f"Quality {quality:.1f}/100 | "
        f"Score {result.get('score',0)} | "
        f"Confidence {confidence:.1f}% | "
        f"RR {rr:.2f}"
    )

    # =====================================
    # RETURN
    # =====================================

    return {

        "analysis": analysis,

        "warnings": warnings,

        "quality": round(quality, 1),

        "rating": rating,

        "recommendation": recommendation,

        "summary": summary

    }
