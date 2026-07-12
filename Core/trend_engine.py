"""
=========================================
BursaAI Smart Trend Engine
Version : 5.0 Institutional
Maximum Score : 35
=========================================
"""


def score_trend(data):

    last = data.iloc[-1]
    prev = data.iloc[-2]

    score = 0
    reason = []

    close = float(last["Close"])
    prev_close = float(prev["Close"])

    ema20 = float(last["EMA20"])
    ema50 = float(last["EMA50"])
    ema200 = float(last["EMA200"])

    ema20_slope = float(last["EMA20_SLOPE"])

    higher_high = bool(last["HIGHER_HIGH"])
    higher_low = bool(last["HIGHER_LOW"])

    breakout = bool(last["BREAKOUT"])

    vwap = float(last["VWAP"])

    # =====================================
    # EMA ALIGNMENT
    # =====================================

    if ema20 > ema50:
        score += 8
        reason.append("EMA20 above EMA50")
    else:
        reason.append("EMA20 below EMA50")

    if ema50 > ema200:
        score += 7
        reason.append("EMA50 above EMA200")
    else:
        reason.append("EMA50 below EMA200")

    # =====================================
    # PRICE LOCATION
    # =====================================

    if close > ema20:
        score += 3
        reason.append("Price above EMA20")

    if close > ema50:
        score += 2
        reason.append("Price above EMA50")

    if close > ema200:
        score += 2
        reason.append("Price above EMA200")

    # =====================================
    # EMA SLOPE
    # =====================================

    if ema20_slope > 0:
        score += 3
        reason.append("EMA20 Rising")

    # =====================================
    # MARKET STRUCTURE
    # =====================================

    if higher_high:
        score += 2
        reason.append("Higher High")

    if higher_low:
        score += 2
        reason.append("Higher Low")

    # =====================================
    # DAILY MOMENTUM
    # =====================================

    if close > prev_close:
        score += 2
        reason.append("Bullish Daily Candle")

    # =====================================
    # VWAP
    # =====================================

    if close > vwap:
        score += 2
        reason.append("Above VWAP")

    # =====================================
    # BREAKOUT
    # =====================================

    if breakout:
        score += 2
        reason.append("20-Day Breakout")

    # =====================================
    # DISTANCE FROM EMA20
    # =====================================

    distance = ((close - ema20) / ema20) * 100

    if 0 <= distance <= 8:
        score += 2
        reason.append("Healthy EMA Distance")

    elif distance > 15:
        score -= 2
        reason.append("Extended From EMA20")

    # =====================================
    # TREND CLASSIFICATION
    # =====================================

    if score >= 30:
        direction = "STRONG UPTREND"

    elif score >= 24:
        direction = "UPTREND"

    elif score >= 17:
        direction = "WEAK UPTREND"

    elif score >= 10:
        direction = "SIDEWAYS"

    else:
        direction = "DOWNTREND"

    return {

        "score": score,

        "direction": direction,

        "ema20": round(ema20, 2),

        "ema50": round(ema50, 2),

        "ema200": round(ema200, 2),

        "distance": round(distance, 2),

        "reason": reason

    }