"""
=========================================
BursaAI Momentum Engine
Version : 5.0 Institutional Stable
=========================================

Maximum Score : 25
"""

from Core.config import (
    MOMENTUM_RSI_STRONG,
    MOMENTUM_RSI_GOOD,
    MOMENTUM_RSI_FAIR,
    MOMENTUM_MACD_BULLISH,
    MOMENTUM_MACD_ABOVE_ZERO
)


def score_momentum(data):

    last = data.iloc[-1]

    score = 0
    reason = []

    rsi = float(last["RSI"])

    macd = float(last["MACD"])
    signal = float(last["MACD_SIGNAL"])

    histogram = float(last.get("MACD_HISTOGRAM", macd - signal))
    roc = float(last.get("ROC", 0))

    # =====================================
    # RSI
    # =====================================

    if 55 <= rsi <= 65:

        score += MOMENTUM_RSI_STRONG
        reason.append("Healthy RSI")

    elif 50 <= rsi < 55:

        score += MOMENTUM_RSI_GOOD
        reason.append("Positive RSI")

    elif 40 <= rsi < 50:

        score += MOMENTUM_RSI_FAIR
        reason.append("Recovering RSI")

    elif 65 < rsi <= 75:

        score += 2
        reason.append("Strong RSI")

    elif rsi > 75:

        score -= 5
        reason.append("Overbought RSI")

    elif rsi < 30:

        score -= 8
        reason.append("Oversold RSI")

    # =====================================
    # MACD
    # =====================================

    if macd > signal:

        score += MOMENTUM_MACD_BULLISH
        reason.append("MACD Bullish")

    else:

        score -= 3
        reason.append("MACD Bearish")

    if macd > 0:

        score += MOMENTUM_MACD_ABOVE_ZERO
        reason.append("MACD Above Zero")

    # =====================================
    # MACD HISTOGRAM
    # =====================================

    if histogram > 0:

        score += 2
        reason.append("Positive Histogram")

    # =====================================
    # ROC
    # =====================================

    if roc > 0:

        score += 2
        reason.append("Positive ROC")

    # =====================================
    # LIMIT SCORE
    # =====================================

    score = max(0, min(score, 25))

    # =====================================
    # QUALITY
    # =====================================

    if score >= 22:

        quality = "STRONG"

    elif score >= 15:

        quality = "GOOD"

    elif score >= 8:

        quality = "FAIR"

    else:

        quality = "WEAK"

    # =====================================
    # RETURN
    # =====================================

    return {

        "score": score,

        "quality": quality,

        "rsi": round(rsi, 2),

        "macd": round(macd, 4),

        "signal": round(signal, 4),

        "histogram": round(histogram, 4),

        "roc": round(roc, 2),

        "reason": reason

    }