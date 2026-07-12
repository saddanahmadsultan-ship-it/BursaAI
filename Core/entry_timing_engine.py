"""
=========================================================
BursaAI Entry Timing Engine
Version : 5.1 Batch 4A
=========================================================
"""

from Core.entry_timing_config import (
    READY_SCORE,
    EARLY_SCORE,
    WAIT_SCORE,
    IDEAL_RSI_MIN,
    IDEAL_RSI_MAX,
    OVERBOUGHT_RSI,
    IDEAL_STOCH_MIN,
    IDEAL_STOCH_MAX,
    OVERBOUGHT_STOCH,
    MAX_EXTENSION_ATR,
)


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_bool(value):
    try:
        return bool(value)
    except Exception:
        return False


def _last_value(last, key, default=0.0):
    try:
        return last.get(key, default)
    except Exception:
        try:
            return last[key]
        except Exception:
            return default


def apply_entry_timing_engine(data, result):
    """
    Menilai kualiti masa kemasukan berdasarkan trend pendek,
    momentum, VWAP, breakout, pullback dan tahap overextended.

    Engine ini tidak menggantikan signal utama. Ia menambah
    lapisan execution timing untuk Position Engine.
    """

    if result is None:
        result = {}

    if data is None or getattr(data, "empty", True):
        return _set_timing(
            result=result,
            score=0.0,
            status="UNKNOWN",
            action="NO DATA",
            zone_low=0.0,
            zone_high=0.0,
            reasons=[],
            warnings=["Entry timing data unavailable"],
        )

    last = data.iloc[-1]

    close = _safe_float(_last_value(last, "Close", 0))
    ema20 = _safe_float(_last_value(last, "EMA20", close))
    ema50 = _safe_float(_last_value(last, "EMA50", close))
    vwap = _safe_float(_last_value(last, "VWAP", close))
    atr = _safe_float(_last_value(last, "ATR", 0))
    ema20_slope = _safe_float(_last_value(last, "EMA20_SLOPE", 0))
    rsi = _safe_float(_last_value(last, "RSI", 50))
    stoch = _safe_float(_last_value(last, "STOCH", 50))
    macd_hist = _safe_float(_last_value(last, "MACD_HISTOGRAM", 0))

    breakout = _safe_bool(_last_value(last, "BREAKOUT", False))
    breakdown = _safe_bool(_last_value(last, "BREAKDOWN", False))
    higher_low = _safe_bool(_last_value(last, "HIGHER_LOW", False))
    higher_high = _safe_bool(_last_value(last, "HIGHER_HIGH", False))

    signal = str(result.get("Signal", "UNKNOWN")).upper().strip()
    regime = str(result.get("MarketRegime", "UNKNOWN")).upper().strip()

    score = 0.0
    reasons = []
    warnings = []

    # Trend alignment.
    if close >= ema20 > 0:
        score += 15
        reasons.append("Price above EMA20")
    else:
        warnings.append("Price below EMA20")

    if ema20 >= ema50 > 0:
        score += 10
        reasons.append("EMA20 above EMA50")

    if ema20_slope > 0:
        score += 10
        reasons.append("EMA20 slope rising")
    else:
        warnings.append("EMA20 slope not rising")

    # VWAP participation.
    if close >= vwap > 0:
        score += 10
        reasons.append("Price above VWAP")
    else:
        warnings.append("Price below VWAP")

    # Momentum confirmation.
    if macd_hist > 0:
        score += 10
        reasons.append("Positive MACD histogram")
    else:
        warnings.append("MACD histogram not positive")

    if IDEAL_RSI_MIN <= rsi <= IDEAL_RSI_MAX:
        score += 15
        reasons.append("RSI in ideal entry zone")
    elif rsi > OVERBOUGHT_RSI:
        score -= 15
        warnings.append("RSI overbought")
    elif rsi >= 35:
        score += 6
        reasons.append("RSI acceptable")
    else:
        warnings.append("RSI weak")

    if IDEAL_STOCH_MIN <= stoch <= IDEAL_STOCH_MAX:
        score += 10
        reasons.append("Stochastic in tradable zone")
    elif stoch > OVERBOUGHT_STOCH:
        score -= 10
        warnings.append("Stochastic overbought")

    # Structure.
    if breakout:
        score += 15
        reasons.append("Breakout confirmation")
    elif higher_low:
        score += 10
        reasons.append("Higher-low support")
    elif higher_high:
        score += 5
        reasons.append("Higher-high structure")

    if breakdown:
        score -= 30
        warnings.append("Breakdown detected")

    # Market regime.
    if regime == "BULLISH":
        score += 10
        reasons.append("Bullish market regime")
    elif regime == "RECOVERY":
        score += 5
        reasons.append("Recovery market regime")
    elif regime in {"WEAK", "BEARISH"}:
        score -= 15
        warnings.append(f"Unfavourable {regime.lower()} regime")

    # Signal context.
    if signal in {"STRONG CONVICTION BUY", "STRONG BUY", "BUY"}:
        score += 5
    elif signal == "HOLD":
        score -= 10
        warnings.append("Signal is HOLD")
    elif signal == "AVOID":
        score = 0
        warnings.append("Signal is AVOID")

    # Avoid chasing an extended price.
    extension_atr = 0.0
    if atr > 0 and ema20 > 0:
        extension_atr = (close - ema20) / atr

        if extension_atr > MAX_EXTENSION_ATR:
            score -= 20
            warnings.append(
                f"Price extended {extension_atr:.2f} ATR above EMA20"
            )

    score = max(0.0, min(round(score, 2), 100.0))

    if signal == "AVOID" or breakdown:
        status = "AVOID"
        action = "NO ENTRY"

    elif score >= READY_SCORE:
        status = "READY"
        action = "ENTER ON CONFIRMATION"

    elif score >= EARLY_SCORE:
        status = "EARLY"

        if extension_atr > MAX_EXTENSION_ATR:
            action = "WAIT PULLBACK"
        else:
            action = "SMALL INITIAL ENTRY"

    elif score >= WAIT_SCORE:
        status = "WAIT"
        action = "WAIT FOR CONFIRMATION"

    else:
        status = "AVOID"
        action = "NO ENTRY"

    # Practical entry zone.
    if close > 0:
        if status == "READY":
            zone_low = min(close, max(vwap, ema20))
            zone_high = close

        elif status in {"EARLY", "WAIT"}:
            support_candidates = [
                value for value in (ema20, vwap)
                if value > 0
            ]
            support = (
                sum(support_candidates) / len(support_candidates)
                if support_candidates
                else close
            )
            zone_low = support - (atr * 0.25 if atr > 0 else 0)
            zone_high = support + (atr * 0.25 if atr > 0 else 0)

        else:
            zone_low = 0.0
            zone_high = 0.0
    else:
        zone_low = 0.0
        zone_high = 0.0

    return _set_timing(
        result=result,
        score=score,
        status=status,
        action=action,
        zone_low=max(round(zone_low, 4), 0.0),
        zone_high=max(round(zone_high, 4), 0.0),
        reasons=reasons,
        warnings=warnings,
    )


def _set_timing(
    result,
    score,
    status,
    action,
    zone_low,
    zone_high,
    reasons,
    warnings,
):
    timing = {
        "score": round(_safe_float(score), 2),
        "status": str(status),
        "action": str(action),
        "entry_zone_low": round(_safe_float(zone_low), 4),
        "entry_zone_high": round(_safe_float(zone_high), 4),
        "reasons": list(reasons or []),
        "warnings": list(warnings or []),
    }

    result["entry_timing"] = timing

    result["EntryTimingScore"] = timing["score"]
    result["EntryTimingStatus"] = timing["status"]
    result["EntryTimingAction"] = timing["action"]
    result["EntryZoneLow"] = timing["entry_zone_low"]
    result["EntryZoneHigh"] = timing["entry_zone_high"]
    result["EntryTimingReasons"] = timing["reasons"]
    result["EntryTimingWarnings"] = timing["warnings"]

    return result