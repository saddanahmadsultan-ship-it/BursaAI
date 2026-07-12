"""
=========================================
BursaAI Volume Engine
Version : 6.0 Institutional Smart Money
Maximum Score : 15
=========================================
"""


def safe_float(value, default=0.0):

    try:
        return float(value)
    except Exception:
        return default


def score_volume(data):

    if data is None or data.empty:

        return {
            "score": 0,
            "strength": "UNKNOWN",
            "ratio": 0,
            "reason": ["No data"]
        }

    last = data.iloc[-1]

    score = 0
    reason = []

    volume = safe_float(last.get("Volume", 0))
    rvol = safe_float(last.get("RVOL", 0))
    rvol5 = safe_float(last.get("RVOL5", 0))

    obv = safe_float(last.get("OBV", 0))
    obv_ma20 = safe_float(last.get("OBV_MA20", 0))

    cmf = safe_float(last.get("CMF", 0))
    mfi = safe_float(last.get("MFI", 50))
    adl = safe_float(last.get("ADL", 0))

    smart_money_score = safe_float(
        last.get("SMART_MONEY_SCORE", 0)
    )

    institutional_buy = bool(
        last.get("INSTITUTIONAL_BUY", False)
    )

    institutional_sell = bool(
        last.get("INSTITUTIONAL_SELL", False)
    )

    accumulation = bool(
        last.get("ACCUMULATION", False)
    )

    distribution = bool(
        last.get("DISTRIBUTION", False)
    )

    volume_spike = bool(
        last.get("VOLUME_SPIKE", False)
    )

    volume_expansion = bool(
        last.get("VOLUME_EXPANSION", False)
    )

    volume_dryup = bool(
        last.get("VOLUME_DRYUP", False)
    )

    above_vwap = bool(
        last.get("ABOVE_VWAP", False)
    )

    breakout = bool(
        last.get("BREAKOUT", False)
    )

    fake_breakout = bool(
        last.get("FAKE_BREAKOUT", False)
    )

    # ==========================
    # VALIDATION
    # ==========================

    if volume <= 0:

        return {
            "score": 0,
            "strength": "WEAK",
            "ratio": 0,
            "reason": ["No volume activity"]
        }

    # ==========================
    # RELATIVE VOLUME
    # ==========================

    if rvol >= 2.5:

        score += 4
        reason.append("Exceptional Relative Volume")

    elif rvol >= 2.0:

        score += 3
        reason.append("Strong Relative Volume")

    elif rvol >= 1.5:

        score += 2
        reason.append("Above Average Volume")

    elif rvol >= 1.0:

        score += 1
        reason.append("Normal Volume")

    elif rvol < 0.5:

        score -= 1
        reason.append("Extremely Low Volume")

    else:

        reason.append("Low Volume")

    # ==========================
    # SHORT TERM VOLUME
    # ==========================

    if rvol5 >= 1.3:

        score += 1
        reason.append("Recent Volume Expansion")

    elif rvol5 < 0.7:

        score -= 1
        reason.append("Recent Volume Dry Up")

    # ==========================
    # OBV CONFIRMATION
    # ==========================

    if obv > obv_ma20:

        score += 2
        reason.append("OBV Above MA20")

    else:

        reason.append("OBV Weak")

    # ==========================
    # CMF / MONEY FLOW
    # ==========================

    if cmf > 0.10:

        score += 2
        reason.append("Strong Positive CMF")

    elif cmf > 0:

        score += 1
        reason.append("Positive CMF")

    elif cmf < -0.10:

        score -= 2
        reason.append("Strong Negative CMF")

    elif cmf < 0:

        score -= 1
        reason.append("Negative CMF")

    # ==========================
    # MFI
    # ==========================

    if 55 <= mfi <= 80:

        score += 2
        reason.append("Healthy Money Flow")

    elif mfi > 80:

        score += 1
        reason.append("High Money Flow")

    elif mfi < 35:

        score -= 1
        reason.append("Weak Money Flow")

    # ==========================
    # SMART MONEY
    # ==========================

    if smart_money_score >= 8:

        score += 3
        reason.append("Strong Smart Money Activity")

    elif smart_money_score >= 5:

        score += 2
        reason.append("Smart Money Activity")

    elif smart_money_score >= 2:

        score += 1
        reason.append("Early Smart Money Signal")

    # ==========================
    # ACCUMULATION / DISTRIBUTION
    # ==========================

    if accumulation:

        score += 2
        reason.append("Accumulation Detected")

    if distribution:

        score -= 2
        reason.append("Distribution Detected")

    if institutional_buy:

        score += 3
        reason.append("Institutional Buying")

    if institutional_sell:

        score -= 3
        reason.append("Institutional Selling")

    # ==========================
    # VWAP
    # ==========================

    if above_vwap:

        score += 1
        reason.append("Price Above VWAP")

    else:

        reason.append("Price Below VWAP")

    # ==========================
    # SPIKE / EXPANSION / DRY UP
    # ==========================

    if volume_spike:

        score += 2
        reason.append("Volume Spike")

    elif volume_expansion:

        score += 1
        reason.append("Volume Expansion")

    if volume_dryup:

        score -= 2
        reason.append("Volume Dry Up")

    # ==========================
    # BREAKOUT QUALITY
    # ==========================

    if breakout and not fake_breakout:

        score += 2
        reason.append("Volume Supported Breakout")

    if fake_breakout:

        score -= 3
        reason.append("Fake Breakout Risk")

    # ==========================
    # FINAL LIMIT
    # ==========================

    score = int(
        max(
            0,
            min(
                15,
                score
            )
        )
    )

    # ==========================
    # CLASSIFICATION
    # ==========================

    if score >= 12:

        strength = "STRONG"

    elif score >= 9:

        strength = "GOOD"

    elif score >= 5:

        strength = "NORMAL"

    else:

        strength = "WEAK"

    return {
        "score": score,
        "strength": strength,
        "ratio": round(rvol, 2),
        "ratio5": round(rvol5, 2),
        "cmf": round(cmf, 3),
        "mfi": round(mfi, 2),
        "adl": round(adl, 2),
        "smart_money_score": round(smart_money_score, 2),
        "institutional_buy": institutional_buy,
        "institutional_sell": institutional_sell,
        "accumulation": accumulation,
        "distribution": distribution,
        "reason": reason
    }