"""
=========================================
BursaAI Risk Management Engine
Version : 3.0 Stable
=========================================
"""

from Core.config import MIN_RR


def calculate_rr(entry, stoploss, target):
    """
    Calculate Risk Reward Ratio.
    Support BUY & SELL.
    """

    if entry is None or stoploss is None or target is None:
        return 0.0

    # BUY
    if stoploss < entry:
        risk = entry - stoploss
        reward = target - entry

    # SELL
    else:
        risk = stoploss - entry
        reward = entry - target

    if risk <= 0:
        return 0.0

    return round(reward / risk, 2)


def is_good_rr(rr):
    """
    Return True jika RR memenuhi syarat minimum.
    """

    return rr >= MIN_RR


def calculate_position_size(capital, risk_percent, entry, stoploss):
    """
    Position sizing berdasarkan risk.
    """

    if capital <= 0:
        return 0

    risk_amount = capital * (risk_percent / 100)

    distance = abs(entry - stoploss)

    if distance == 0:
        return 0

    units = risk_amount / distance

    return int(units)


def calculate_risk_percent(entry, stoploss):
    """
    Risk dalam %.
    """

    if entry == 0:
        return 0

    return round(abs(entry - stoploss) / entry * 100, 2)


def risk_level(rr):
    """
    Classification Risk Reward
    """

    if rr >= 3:
        return "Excellent"

    elif rr >= 2:
        return "Good"

    elif rr >= 1.5:
        return "Average"

    return "Poor"