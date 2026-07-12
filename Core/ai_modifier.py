"""
=========================================
BursaAI AI Modifier Engine
Version : 2.0 Institutional
=========================================

Purpose:
Apply institutional bonus & penalty
after all scoring engines finish.

Maximum Modifier :
+20
-20
"""


def apply_ai_modifier(

    trend_data,
    momentum_data,
    volume_data,
    volatility_data,
    risk_data

):

    bonus = 0
    penalty = 0

    reason = []

    # =====================================
    # TREND
    # =====================================

    trend = trend_data.get("direction", "UNKNOWN")

    if trend == "STRONG UPTREND":

        bonus += 6
        reason.append("+6 Strong Uptrend")

    elif trend == "UPTREND":

        bonus += 3
        reason.append("+3 Uptrend")

    elif trend == "WEAK UPTREND":

        bonus += 1
        reason.append("+1 Weak Uptrend")

    elif trend == "SIDEWAYS":

        penalty += 4
        reason.append("-4 Sideways")

    else:

        penalty += 8
        reason.append("-8 Downtrend")

    # =====================================
    # MOMENTUM
    # =====================================

    momentum = momentum_data.get("quality", "WEAK")

    if momentum == "STRONG":

        bonus += 5
        reason.append("+5 Strong Momentum")

    elif momentum == "GOOD":

        bonus += 3
        reason.append("+3 Good Momentum")

    elif momentum == "FAIR":

        bonus += 1

    else:

        penalty += 4
        reason.append("-4 Weak Momentum")

    # =====================================
    # VOLUME
    # =====================================

    volume = volume_data.get("strength", "WEAK")

    if volume == "STRONG":

        bonus += 5
        reason.append("+5 Strong Volume")

    elif volume == "GOOD":

        bonus += 3
        reason.append("+3 Good Volume")

    elif volume == "NORMAL":

        bonus += 1

    else:

        penalty += 5
        reason.append("-5 Weak Volume")

    # =====================================
    # VOLATILITY
    # =====================================

    quality = volatility_data.get("quality", "HIGH")

    if quality == "LOW":

        bonus += 2
        reason.append("+2 Stable Volatility")

    elif quality == "MEDIUM":

        bonus += 1
        reason.append("+1 Healthy Volatility")

    elif quality == "HIGH":

        penalty += 2
        reason.append("-2 High Volatility")

    elif quality == "EXTREME":

        penalty += 5
        reason.append("-5 Extreme Volatility")

    # =====================================
    # RISK REWARD
    # =====================================

    rr = risk_data.get("rr", 0)

    if rr >= 3:

        bonus += 4
        reason.append("+4 Excellent RR")

    elif rr >= 2:

        bonus += 2
        reason.append("+2 Good RR")

    elif rr >= 1.5:

        pass

    else:

        penalty += 5
        reason.append("-5 Poor RR")

    # =====================================
    # FINAL MODIFIER
    # =====================================

    modifier = bonus - penalty

    modifier = max(-20, min(20, modifier))

    return {

        "bonus": bonus,

        "penalty": penalty,

        "modifier": modifier,

        "reason": reason

    }