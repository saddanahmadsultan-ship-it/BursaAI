"""
=========================================
BursaAI Confidence Engine
Version : 2.0 Institutional
=========================================
"""


def calculate_confidence(

    trend_data,
    momentum_data,
    volume_data,
    volatility_data,
    risk_data,
    modifier_data

):

    confidence = 50

    reason = []

    # =====================================
    # TREND
    # =====================================

    trend = trend_data["direction"]

    if trend == "STRONG UPTREND":
        confidence += 18
        reason.append("Strong Trend")

    elif trend == "UPTREND":
        confidence += 12
        reason.append("Uptrend")

    elif trend == "WEAK UPTREND":
        confidence += 6
        reason.append("Weak Uptrend")

    elif trend == "SIDEWAYS":
        confidence -= 8
        reason.append("Sideways")

    else:
        confidence -= 18
        reason.append("Downtrend")

    # =====================================
    # MOMENTUM
    # =====================================

    momentum = momentum_data["quality"]

    if momentum == "STRONG":
        confidence += 12
        reason.append("Strong Momentum")

    elif momentum == "GOOD":
        confidence += 8

    elif momentum == "FAIR":
        confidence += 3

    else:
        confidence -= 8

    # =====================================
    # VOLUME
    # =====================================

    volume = volume_data["strength"]

    if volume == "STRONG":
        confidence += 10

    elif volume == "GOOD":
        confidence += 6

    elif volume == "NORMAL":
        confidence += 2

    else:
        confidence -= 6

    # =====================================
    # VOLATILITY
    # =====================================

    vol = volatility_data["level"]

    if vol == "STABLE":
        confidence += 6

    elif vol == "NORMAL":
        confidence += 3

    elif vol == "HIGH":
        confidence -= 3

    else:
        confidence -= 8

    # =====================================
    # RISK REWARD
    # =====================================

    rr = risk_data["rr"]

    if rr >= 3:
        confidence += 10

    elif rr >= 2:
        confidence += 6

    elif rr >= 1.5:
        confidence += 2

    else:
        confidence -= 8

    # =====================================
    # AI MODIFIER
    # =====================================

    confidence += modifier_data["modifier"]

    if modifier_data["modifier"] > 0:
        reason.append("Positive AI Modifier")

    elif modifier_data["modifier"] < 0:
        reason.append("Negative AI Modifier")

    # =====================================
    # LIMIT
    # =====================================

    confidence = max(0, min(100, confidence))

    # =====================================
    # LEVEL
    # =====================================

    if confidence >= 90:
        level = "VERY HIGH"

    elif confidence >= 75:
        level = "HIGH"

    elif confidence >= 60:
        level = "MEDIUM"

    elif confidence >= 45:
        level = "LOW"

    else:
        level = "VERY LOW"

    return {

        "confidence": round(confidence, 1),

        "level": level,

        "reason": reason

    }