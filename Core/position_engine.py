"""
====================================================
BursaAI Position Sizing Engine
Version : 5.2 Batch 4B Dynamic Risk
====================================================
"""

import math

from Core.portfolio_config import (
    get_portfolio_config
)



def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _round_money(value):
    return round(
        _safe_float(value, 0.0),
        2
    )


def _reset_position_fields(result, status="SKIP"):
    result["AccountCapital"] = 0.0
    result["RiskPercent"] = 0.0
    result["RiskCapital"] = 0.0
    result["RiskPerShare"] = 0.0

    result["Shares"] = 0
    result["Lots"] = 0

    result["Capital"] = 0.0
    result["CapitalUsed"] = 0.0
    result["RemainingCapital"] = 0.0

    result["Allocation"] = 0.0
    result["MaxLoss"] = 0.0
    result["PotentialProfit"] = 0.0

    result["PositionStatus"] = status
    result["PositionRating"] = "SKIP"

    return result


def apply_position_engine(result):
    """
    Calculate position size using:

    Account capital
    Risk per trade
    Entry price
    Stop-loss price
    Target price
    Signal quality
    Maximum position allocation
    """

    if result is None:
        result = {}

    config = get_portfolio_config()

    capital = _safe_float(
        config.get("capital", 0)
    )

    base_risk_percent = _safe_float(
        config.get("risk_percent", 0)
    )

    max_position_percent = _safe_float(
        config.get(
            "max_position_percent",
            0
        )
    )

    min_position_percent = _safe_float(
        config.get(
            "min_position_percent",
            0
        )
    )

    lot_size = _safe_int(
        config.get("lot_size", 100),
        100
    )

    round_lot = bool(
        config.get("round_lot", True)
    )

    minimum_final_score = _safe_float(
        config.get(
            "minimum_final_score",
            0
        )
    )

    minimum_confidence = _safe_float(
        config.get(
            "minimum_confidence",
            0
        )
    )

    minimum_rr = _safe_float(
        config.get(
            "minimum_risk_reward",
            0
        )
    )

    signal_multipliers = config.get(
        "signal_risk_multiplier",
        {}
    )

    signal = str(
        result.get("Signal", "UNKNOWN")
    ).upper().strip()

    timing_status = str(
        result.get(
            "EntryTimingStatus",
            result.get("entry_timing", {}).get("status", "UNKNOWN")
        )
    ).upper().strip()

    dynamic_risk_percent = _safe_float(
        result.get("DynamicRiskPercent", 0)
    )

    dynamic_risk_status = str(
        result.get("DynamicRiskStatus", "BLOCKED")
    ).upper().strip()

    entry = _safe_float(
        result.get("Entry", 0)
    )

    stop_loss = _safe_float(
        result.get("StopLoss", 0)
    )

    target = _safe_float(
        result.get("Target", 0)
    )

    rr = _safe_float(
        result.get("RR", 0)
    )

    final_score = _safe_float(
        result.get(
            "FinalScore",
            result.get("Score", 0)
        )
    )

    confidence = _safe_float(
        result.get("Confidence", 0)
    )

    # ==========================================
    # BASE ACCOUNT DATA
    # ==========================================

    result["AccountCapital"] = _round_money(
        capital
    )

    result["RemainingCapital"] = _round_money(
        capital
    )

    # ==========================================
    # BASIC VALIDATION
    # ==========================================

    if capital <= 0:
        return _reset_position_fields(
            result,
            "INVALID CAPITAL"
        )

    if signal == "AVOID":
        result = _reset_position_fields(
            result,
            "SKIP - AVOID"
        )

        result["AccountCapital"] = _round_money(
            capital
        )

        result["RemainingCapital"] = _round_money(
            capital
        )

        return result

    if entry <= 0:
        result = _reset_position_fields(
            result,
            "INVALID ENTRY"
        )

        result["AccountCapital"] = _round_money(
            capital
        )

        result["RemainingCapital"] = _round_money(
            capital
        )

        return result

    if stop_loss <= 0:
        result = _reset_position_fields(
            result,
            "INVALID STOP LOSS"
        )

        result["AccountCapital"] = _round_money(
            capital
        )

        result["RemainingCapital"] = _round_money(
            capital
        )

        return result

    if stop_loss >= entry:
        result = _reset_position_fields(
            result,
            "INVALID RISK"
        )

        result["AccountCapital"] = _round_money(
            capital
        )

        result["RemainingCapital"] = _round_money(
            capital
        )

        return result

    if final_score < minimum_final_score:
        result = _reset_position_fields(
            result,
            "SKIP - LOW SCORE"
        )

        result["AccountCapital"] = _round_money(
            capital
        )

        result["RemainingCapital"] = _round_money(
            capital
        )

        return result

    if confidence < minimum_confidence:
        result = _reset_position_fields(
            result,
            "SKIP - LOW CONFIDENCE"
        )

        result["AccountCapital"] = _round_money(
            capital
        )

        result["RemainingCapital"] = _round_money(
            capital
        )

        return result

    if rr < minimum_rr:
        result = _reset_position_fields(
            result,
            "SKIP - POOR RR"
        )

        result["AccountCapital"] = _round_money(
            capital
        )

        result["RemainingCapital"] = _round_money(
            capital
        )

        return result

    # ==========================================
    # SIGNAL RISK MULTIPLIER
    # ==========================================

    risk_multiplier = _safe_float(
        signal_multipliers.get(
            signal,
            signal_multipliers.get(
                "UNKNOWN",
                0
            )
        )
    )

    # Batch 4B: Dynamic Risk Manager has already combined
    # signal, timing, regime, volatility, confidence, score,
    # risk-reward and smart-money multipliers.
    effective_risk_percent = dynamic_risk_percent

    if effective_risk_percent <= 0 or dynamic_risk_status == "BLOCKED":
        if timing_status in {"AVOID", "UNKNOWN"}:
            skip_reason = "SKIP - TIMING"
        elif risk_multiplier <= 0:
            skip_reason = "SKIP - SIGNAL"
        else:
            skip_reason = "SKIP - DYNAMIC RISK"

        result = _reset_position_fields(
            result,
            skip_reason
        )

        result["AccountCapital"] = _round_money(
            capital
        )

        result["RemainingCapital"] = _round_money(
            capital
        )

        return result

    # ==========================================
    # RISK CALCULATION
    # ==========================================

    risk_capital = (
        capital *
        effective_risk_percent /
        100
    )

    risk_per_share = abs(
        entry - stop_loss
    )

    if risk_per_share <= 0:
        result = _reset_position_fields(
            result,
            "INVALID RISK"
        )

        result["AccountCapital"] = _round_money(
            capital
        )

        result["RemainingCapital"] = _round_money(
            capital
        )

        return result

    risk_based_shares = math.floor(
        risk_capital /
        risk_per_share
    )

    # ==========================================
    # MAXIMUM POSITION LIMIT
    # ==========================================

    maximum_position_value = (
        capital *
        max_position_percent /
        100
    )

    allocation_based_shares = math.floor(
        maximum_position_value /
        entry
    )

    shares = min(
        risk_based_shares,
        allocation_based_shares
    )

    # ==========================================
    # ROUND TO BURSA LOT
    # ==========================================

    if round_lot and lot_size > 0:

        lots = math.floor(
            shares /
            lot_size
        )

        shares = lots * lot_size

    else:

        lots = shares

    if shares <= 0:
        result = _reset_position_fields(
            result,
            "SKIP - SIZE TOO SMALL"
        )

        result["AccountCapital"] = _round_money(
            capital
        )

        result["RiskPercent"] = round(
            effective_risk_percent,
            2
        )

        result["RiskCapital"] = _round_money(
            risk_capital
        )

        result["RiskPerShare"] = _round_money(
            risk_per_share
        )

        result["RemainingCapital"] = _round_money(
            capital
        )

        return result

    # ==========================================
    # FINAL POSITION VALUES
    # ==========================================

    capital_used = shares * entry

    remaining_capital = (
        capital -
        capital_used
    )

    max_loss = (
        shares *
        risk_per_share
    )

    if target > entry:

        potential_profit = (
            shares *
            (target - entry)
        )

    else:

        potential_profit = 0.0

    allocation_percent = (
        capital_used /
        capital *
        100
    )

    actual_risk_percent = (
        max_loss /
        capital *
        100
    )

    # ==========================================
    # POSITION STATUS
    # ==========================================

    if allocation_percent < min_position_percent:

        position_status = "SMALL POSITION"

    elif signal in (
        "STRONG BUY",
        "BUY"
    ):

        position_status = "READY"

    elif signal == "WATCH":

        position_status = "WATCH POSITION"

    elif signal == "HOLD":

        position_status = "HOLD POSITION"

    else:

        position_status = "REVIEW"

    # ==========================================
    # POSITION RATING
    # ==========================================

    if (
        final_score >= 80
        and confidence >= 75
        and rr >= 2
    ):

        position_rating = "STRONG"

    elif (
        final_score >= 70
        and confidence >= 65
        and rr >= 1.8
    ):

        position_rating = "GOOD"

    elif (
        final_score >= 60
        and confidence >= 55
        and rr >= 1.5
    ):

        position_rating = "MODERATE"

    else:

        position_rating = "CAUTIOUS"

    # ==========================================
    # RESULT
    # ==========================================

    result["AccountCapital"] = _round_money(
        capital
    )

    result["RiskPercent"] = round(
        effective_risk_percent,
        2
    )

    result["RiskCapital"] = _round_money(
        risk_capital
    )

    result["RiskPerShare"] = _round_money(
        risk_per_share
    )

    result["Shares"] = int(shares)

    result["Lots"] = int(lots)

    result["Capital"] = _round_money(
        capital_used
    )

    result["CapitalUsed"] = _round_money(
        capital_used
    )

    result["RemainingCapital"] = _round_money(
        remaining_capital
    )

    result["Allocation"] = round(
        allocation_percent,
        2
    )

    result["ActualRiskPercent"] = round(
        actual_risk_percent,
        2
    )

    result["MaxLoss"] = _round_money(
        max_loss
    )

    result["PotentialProfit"] = _round_money(
        potential_profit
    )

    result["PositionStatus"] = (
        position_status
    )

    result["PositionRating"] = (
        position_rating
    )

    return result