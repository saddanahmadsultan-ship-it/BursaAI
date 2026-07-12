"""
=========================================
BursaAI AI Weighted Score Engine
Version : 5.0 Institutional
=========================================
"""

from Core.trend_engine import score_trend
from Core.momentum_engine import score_momentum
from Core.volume_engine import score_volume
from Core.volatility_engine import score_volatility
from Core.risk_engine import score_risk
from Core.ai_modifier import apply_ai_modifier

from Core.config import (
    DEFAULT_STOPLOSS_ATR,
    DEFAULT_TARGET_ATR,
    DEBUG_SCORE
)


# ==================================================
# SAFE ENGINE
# ==================================================

def safe_engine(func, *args):

    try:

        result = func(*args)

        if isinstance(result, dict):

            result.setdefault("score", 0)
            result.setdefault("reason", [])

            return result

        elif isinstance(result, tuple):

            score = result[0]
            reason = result[1]

            return {

                "score": score,

                "reason": reason

            }

        return {

            "score": 0,

            "reason": ["Invalid Engine Output"]

        }

    except Exception as e:

        return {

            "score": 0,

            "reason": [str(e)]

        }


# ==================================================
# NORMALIZE
# ==================================================

def normalize(value, maximum):

    if maximum <= 0:

        return 0

    return (value / maximum) * 100


# ==================================================
# MAIN AI SCORE
# ==================================================

def calculate_score(

    data,

    entry=None,

    stoploss=None,

    target=None

):

    last = data.iloc[-1]

    close = float(last["Close"])

    atr = float(last["ATR"])

    # ===========================================
    # AUTO ENTRY
    # ===========================================

    if entry is None:

        entry = round(close, 2)

    if stoploss is None:

        stoploss = round(close - (

            DEFAULT_STOPLOSS_ATR * atr

        ), 2)

    if target is None:

        target = round(close + (

            DEFAULT_TARGET_ATR * atr

        ), 2)

    # ===========================================
    # ENGINES
    # ===========================================

    trend = safe_engine(

        score_trend,

        data

    )

    momentum = safe_engine(

        score_momentum,

        data

    )

    volume = safe_engine(

        score_volume,

        data

    )

    volatility = safe_engine(

        score_volatility,

        data

    )

    risk = safe_engine(

        score_risk,

        entry,

        stoploss,

        target

    )

    # ===========================================
    # DEBUG
    # ===========================================

    if DEBUG_SCORE:

        print()

        print("DEBUG SCORE")

        print("TREND      :", trend["score"])

        print("MOMENTUM   :", momentum["score"])

        print("VOLUME     :", volume["score"])

        print("VOLATILITY :", volatility["score"])

        print("RISK       :", risk["score"])

    # ===========================================
    # WEIGHTED SCORE
    # ===========================================

    trend_score = normalize(

        trend["score"],

        35

    )

    momentum_score = normalize(

        momentum["score"],

        25

    )

    volume_score = normalize(

        volume["score"],

        15

    )

    volatility_score = normalize(

        volatility["score"],

        10

    )

    risk_score = normalize(

        risk["score"],

        15

    )

    base_score = (

        trend_score * 0.35 +

        momentum_score * 0.25 +

        volume_score * 0.15 +

        volatility_score * 0.10 +

        risk_score * 0.15

    )

    base_score = round(

        max(

            0,

            min(

                100,

                base_score

            )

        )

    )

    # ===========================================
    # AI MODIFIER
    # ===========================================

    modifier = apply_ai_modifier(
        trend,
        momentum,
        volume,
        volatility,
        risk
    )

    final_score = (

        base_score +

        modifier["modifier"]

    )

    final_score = round(

        max(

            0,

            min(

                100,

                final_score

            )

        )

    )

    # ===========================================
    # GRADE
    # ===========================================

    if final_score >= 90:

        grade = "A+"

    elif final_score >= 80:

        grade = "A"

    elif final_score >= 70:

        grade = "B+"

    elif final_score >= 60:

        grade = "B"

    elif final_score >= 50:

        grade = "C"

    else:

        grade = "D"

    # ===========================================
    # REASONS
    # ===========================================

    reason = (

        trend["reason"]

        +

        momentum["reason"]

        +

        volume["reason"]

        +

        volatility["reason"]

        +

        risk["reason"]

    )

    # ===========================================
    # RETURN
    # ===========================================

    return {

        "score": final_score,

        "base_score": base_score,

        "modifier": modifier["modifier"],

        "bonus": modifier["bonus"],

        "penalty": modifier["penalty"],

        "modifier_reason": modifier["reason"],

        "grade": grade,

        "trend": trend,

        "momentum": momentum,

        "volume": volume,

        "volatility": volatility,

        "risk": risk,

        "entry": round(entry, 2),

        "stoploss": round(stoploss, 2),

        "target": round(target, 2),

        "reason": reason

    }
