"""
=========================================
BursaAI Strategy Engine
Version : 4.1 Institutional Stable
=========================================
"""

from Core.config import (
    DEFAULT_STOPLOSS_ATR,
    DEFAULT_TARGET_ATR
)

from Core.risk import calculate_rr


def trading_signal(
    data,
    score_data,
    trend_data,
    momentum_data,
    volume_data,
    confidence_data
):

    last = data.iloc[-1]

    close = float(last["Close"])
    ma20 = float(last["MA20"])
    ma50 = float(last["MA50"])
    ma200 = float(last["MA200"])

    atr = float(last["ATR"])

    rsi = float(last["RSI"])
    macd = float(last["MACD"])
    macd_signal = float(last["MACD_SIGNAL"])

    score = score_data["score"]
    confidence = confidence_data["confidence"]

    trend = trend_data["direction"]

    momentum = momentum_data.get("quality", "FAIR")

    volume_score = volume_data.get("score", 0)

    if volume_score >= 12:
        volume = "STRONG"
    elif volume_score >= 8:
        volume = "GOOD"
    elif volume_score >= 4:
        volume = "FAIR"
    else:
        volume = "WEAK"
    # ======================================
    # MARKET STRUCTURE
    # ======================================

    bullish = (
        close > ma20 and
        ma20 > ma50 and
        ma50 > ma200
    )

    bearish = (
        close < ma20 and
        ma20 < ma50 and
        ma50 < ma200
    )

    sideways = not bullish and not bearish

    # ======================================
    # TRADE PLAN
    # ======================================

    entry = round(close, 2)

    stoploss = round(
        close - (DEFAULT_STOPLOSS_ATR * atr),
        2
    )

    target = round(
        close + (DEFAULT_TARGET_ATR * atr),
        2
    )

    rr = calculate_rr(
        entry,
        stoploss,
        target
    )

    # ======================================
    # INSTITUTIONAL DECISION
    # ======================================

    if (
        bullish
        and trend == "STRONG UPTREND"
        and momentum in ("GOOD", "STRONG")
        and volume in ("GOOD", "STRONG")
        and score >= 70
        and confidence >= 75
        and rr >= 2
    ):

        strategy = "STRONG BUY"

    elif (
        trend in ("UPTREND", "STRONG UPTREND")
        and momentum in ("FAIR", "GOOD", "STRONG")
        and score >= 55
        and confidence >= 50
        and rr >= 2
    ):

        strategy = "BUY"

    elif (
        score >= 45
        and confidence >= 40
    ):

        strategy = "WATCH"

    elif score >= 30:

        strategy = "HOLD"

    else:

        strategy = "AVOID"

    # ======================================
    # WARNING ENGINE
    # ======================================

    warning = []

    if rsi > 70:
        warning.append("RSI Overbought")

    if rsi < 30:
        warning.append("RSI Oversold")

    if macd < macd_signal:
        warning.append("MACD Bearish")

    if volume == "WEAK":
        warning.append("Weak Volume")

    if momentum == "WEAK":
        warning.append("Weak Momentum")

    if confidence < 40:
        warning.append("Low Confidence")

    if rr < 2:
        warning.append("Poor Risk Reward")

    if bearish:
        warning.append("Bearish Structure")

    if sideways:
        warning.append("Sideways Market")

    return {

        "strategy": strategy,

        "entry": entry,

        "stoploss": stoploss,

        "target": target,

        "rr": rr,

        "bullish": bullish,

        "warning": warning

    }
