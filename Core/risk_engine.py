"""
=========================================
BursaAI Risk Engine
Version : 2.0 Stable
=========================================

Maximum Score : 15
"""

from Core.risk import (
    calculate_rr,
    risk_level,
    is_good_rr
)


def score_risk(entry, stoploss, target):

    # ==========================
    # VALIDATION
    # ==========================

    if entry <= 0 or stoploss <= 0 or target <= 0:

        return {

            "score": 0,

            "rr": 0,

            "level": "INVALID",

            "good": False,

            "reason": [
                "Invalid Entry / Stop Loss / Target"
            ]

        }

    # ==========================
    # RISK REWARD
    # ==========================

    rr = calculate_rr(
        entry,
        stoploss,
        target
    )

    # ==========================
    # SCORE
    # ==========================

    if rr >= 3:

        score = 15
        text = "Excellent Risk Reward"

    elif rr >= 2:

        score = 12
        text = "Good Risk Reward"

    elif rr >= 1.5:

        score = 8
        text = "Moderate Risk Reward"

    elif rr >= 1:

        score = 5
        text = "Low Risk Reward"

    else:

        score = 2
        text = "Poor Risk Reward"

    # ==========================
    # RETURN
    # ==========================

    return {

        "score": score,

        "rr": round(rr, 2),

        "level": risk_level(rr),

        "good": is_good_rr(rr),

        "reason": [
            f"{text} (RR {rr:.2f})"
        ]

    }