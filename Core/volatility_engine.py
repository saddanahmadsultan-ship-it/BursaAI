"""
=========================================
BursaAI Volatility Engine
Version : 5.0 Core Refactor Stable
=========================================
"""

from Core.config import (
    VOLATILITY_LOW,
    VOLATILITY_MEDIUM,
    VOLATILITY_HIGH,
    VOLATILITY_EXTREME
)


def score_volatility(data):

    last = data.iloc[-1]

    atr = float(last["ATR"])
    close = float(last["Close"])

    if close <= 0:
        return {
            "score": 0,
            "quality": "UNKNOWN",
            "level": "UNKNOWN",
            "atr_percent": 0,
            "reason": ["Invalid Close Price"]
        }

    atr_percent = (atr / close) * 100

    if atr_percent <= 2:

        score = VOLATILITY_LOW
        quality = "LOW"
        level = "STABLE"

    elif atr_percent <= 4:

        score = VOLATILITY_MEDIUM
        quality = "MEDIUM"
        level = "NORMAL"

    elif atr_percent <= 6:

        score = VOLATILITY_HIGH
        quality = "HIGH"
        level = "HIGH"

    else:

        score = VOLATILITY_EXTREME
        quality = "EXTREME"
        level = "EXTREME"

    reason = [
        f"ATR = {atr_percent:.2f}%"
    ]

    if atr_percent <= 2:
        reason.append("Stable Price Movement")

    elif atr_percent <= 4:
        reason.append("Healthy Volatility")

    elif atr_percent <= 6:
        reason.append("High Volatility")

    else:
        reason.append("Extreme Volatility")

    return {

        "score": score,

        "quality": quality,

        "level": level,

        "atr": round(atr, 4),

        "atr_percent": round(atr_percent, 2),

        "reason": reason

    }