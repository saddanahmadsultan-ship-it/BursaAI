"""
=========================================
BursaAI Smart Quality Filter
Version : 2.0 Institutional
=========================================
"""


def validate_trade(
    trend_data,
    momentum_data,
    volume_data,
    confidence_data,
    strategy_data,
    decision_data
):

    signal = decision_data["recommendation"]

    reasons = []

    penalty = 0

    trend = trend_data["direction"]
    trend_score = trend_data["score"]

    momentum = momentum_data["quality"]
    momentum_score = momentum_data["score"]

    volume = volume_data["strength"]
    volume_score = volume_data["score"]

    confidence = confidence_data["confidence"]

    rr = strategy_data["rr"]

    bullish = strategy_data["bullish"]

    # =====================================
    # MARKET STRUCTURE
    # =====================================

    if not bullish:
        penalty += 2
        reasons.append("Market structure not bullish")

    # =====================================
    # TREND
    # =====================================

    if trend == "DOWNTREND":
        penalty += 4
        reasons.append("Downtrend")

    elif trend == "SIDEWAYS":
        penalty += 2
        reasons.append("Sideways")

    elif trend == "WEAK UPTREND":
        penalty += 1
        reasons.append("Weak Uptrend")

    if trend_score < 15:
        penalty += 1
        reasons.append("Low Trend Score")

    # =====================================
    # MOMENTUM
    # =====================================

    if momentum == "WEAK":
        penalty += 2
        reasons.append("Weak Momentum")

    elif momentum == "FAIR":
        penalty += 1
        reasons.append("Average Momentum")

    if momentum_score < 8:
        penalty += 1

    # =====================================
    # VOLUME
    # =====================================

    if volume == "WEAK":
        penalty += 2
        reasons.append("Weak Volume")

    elif volume == "NORMAL":
        penalty += 1

    if volume_score < 5:
        penalty += 1

    # =====================================
    # CONFIDENCE
    # =====================================

    if confidence < 40:
        penalty += 4
        reasons.append("Very Low Confidence")

    elif confidence < 55:
        penalty += 2
        reasons.append("Low Confidence")

    elif confidence < 70:
        penalty += 1

    # =====================================
    # RISK REWARD
    # =====================================

    if rr < 1.5:
        penalty += 3
        reasons.append("Poor RR")

    elif rr < 2:
        penalty += 2
        reasons.append("RR Below 2")

    # =====================================
    # FINAL FILTER
    # =====================================

    if penalty >= 9:

        signal = "AVOID"

    elif penalty >= 6:

        signal = "HOLD"

    elif penalty >= 3:

        signal = "WATCH"

    return {

        "signal": signal,

        "penalty": penalty,

        "reason": reasons

    }
