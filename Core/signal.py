
"""
=========================================
BursaAI Signal Engine
Version : 3.2 AI Weighted Signal
=========================================
"""


def score_to_signal(
        score,
        trend=None,
        quality=0
):


    if quality >= 75:

        return "STRONG BUY"


    elif quality >= 60:

        return "BUY"


    elif quality >= 45:

        return "WATCH"


    elif quality >= 30:

        return "HOLD"


    else:

        return "AVOID"
