"""
=========================================================
BursaAI Result Model
Version : 5.0 Batch 3D Compatible
=========================================================
"""

from __future__ import annotations

from typing import Any, Dict, Iterable


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _safe_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def _safe_list(value: Any) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, set):
        return list(value)
    if isinstance(value, str):
        return [value] if value.strip() else []
    return [value]


def _first(mapping: Dict[str, Any], keys: Iterable[str], default: Any = None) -> Any:
    if not isinstance(mapping, dict):
        return default

    for key in keys:
        if key in mapping and mapping[key] is not None:
            return mapping[key]

    return default


def _grade_from_score(score: float) -> str:
    if score >= 90:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B+"
    if score >= 60:
        return "B"
    if score >= 50:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def build_result(
    symbol,
    last,
    score_data,
    trend_data,
    momentum_data,
    volume_data,
    volatility_data,
    risk_data,
    confidence_data,
    strategy_data,
    decision_data,
    validator
):
    """
    Bina result standard BursaAI.

    Struktur ini menyediakan:
    1. Alias rata untuk engine lama.
    2. Struktur nested untuk main.py dan exporter v5.
    """

    score_data = score_data or {}
    trend_data = trend_data or {}
    momentum_data = momentum_data or {}
    volume_data = volume_data or {}
    volatility_data = volatility_data or {}
    risk_data = risk_data or {}
    confidence_data = confidence_data or {}
    strategy_data = strategy_data or {}
    decision_data = decision_data or {}
    validator = validator or {}

    price = _safe_float(
        last.get("Close", 0) if hasattr(last, "get") else 0
    )

    rsi = _safe_float(
        last.get("RSI", 0) if hasattr(last, "get") else 0
    )

    raw_score = _safe_float(
        _first(score_data, ["score", "raw_score", "raw"], 0)
    )

    grade = _safe_text(
        _first(score_data, ["grade"], _grade_from_score(raw_score))
    )

    confidence_value = _safe_float(
        _first(confidence_data, ["confidence", "value"], 0)
    )

    confidence_level = _safe_text(
        _first(confidence_data, ["level"], "UNKNOWN")
    )

    trend = _safe_text(
        _first(trend_data, ["direction", "quality"], "UNKNOWN")
    )

    volume = _safe_text(
        _first(volume_data, ["strength", "quality"], "UNKNOWN")
    )

    decision_signal = _safe_text(
        _first(
            decision_data,
            ["recommendation", "signal", "decision"],
            "UNKNOWN"
        )
    )

    validated_signal = _safe_text(
        _first(validator, ["signal"], decision_signal)
    )

    validation_penalty = _safe_float(
        _first(validator, ["penalty"], 0)
    )

    validation_reasons = _safe_list(
        _first(validator, ["reason", "reasons"], [])
    )

    rating = _safe_text(
        _first(decision_data, ["rating"], "UNKNOWN")
    )

    entry = _safe_float(
        _first(strategy_data, ["entry", "entry_price"], price)
    )

    stop_loss = _safe_float(
        _first(
            strategy_data,
            ["stoploss", "stop_loss", "sl"],
            0
        )
    )

    target = _safe_float(
        _first(strategy_data, ["target", "target_price"], 0)
    )

    rr = _safe_float(
        _first(strategy_data, ["rr", "risk_reward"], 0)
    )

    score_reasons = _safe_list(
        _first(score_data, ["reason", "reasons"], [])
    )

    warnings = _safe_list(
        _first(strategy_data, ["warning", "warnings"], [])
    )

    summary = _safe_text(
        _first(decision_data, ["summary"], "")
    )

    analysis_reasons = _safe_list(
        _first(
            decision_data,
            ["reason", "reasons", "analysis"],
            score_reasons
        )
    )

    analysis_warnings = _safe_list(
        _first(
            decision_data,
            ["warning", "warnings"],
            warnings
        )
    )

    result = {
        # =====================================
        # FLAT LEGACY FIELDS
        # =====================================
        "Code": _safe_text(symbol),
        "Price": round(price, 2),

        "RawScore": round(raw_score, 2),
        "Score": round(raw_score, 2),
        "QualityPenalty": 0.0,
        "TradeableScore": round(raw_score, 2),
        "InstitutionBonus": 0.0,
        "RegimeScore": 0.0,
        "RegimeBonus": 0.0,
        "RegimePenalty": 0.0,
        "FinalScore": round(raw_score, 2),
        "Grade": grade,

        "Confidence": round(confidence_value, 2),
        "ConfLevel": confidence_level,

        "Trend": trend,
        "Volume": volume,
        "SmartMoney": "NONE",
        "MarketRegime": "UNKNOWN",

        "DecisionSignal": decision_signal,
        "Signal": validated_signal,
        "Rating": rating,

        "Validation": round(validation_penalty, 2),
        "ValidationReason": ", ".join(
            _safe_text(reason) for reason in validation_reasons
        ),

        "Entry": round(entry, 4),
        "StopLoss": round(stop_loss, 4),
        "Target": round(target, 4),
        "RR": round(rr, 2),
        "RSI": round(rsi, 2),

        "Reason": score_reasons,
        "Warning": warnings,
        "Summary": summary,

        # =====================================
        # POSITION DEFAULTS
        # =====================================
        "AccountCapital": 0.0,
        "RiskPercent": 0.0,
        "RiskCapital": 0.0,
        "RiskPerShare": 0.0,
        "Shares": 0,
        "Lots": 0,
        "Capital": 0.0,
        "CapitalUsed": 0.0,
        "RemainingCapital": 0.0,
        "Allocation": 0.0,
        "ActualRiskPercent": 0.0,
        "MaxLoss": 0.0,
        "PotentialProfit": 0.0,
        "PositionStatus": "PENDING",
        "PositionRating": "NONE",

        # =====================================
        # PORTFOLIO DEFAULTS
        # =====================================
        "PortfolioEligible": False,
        "PortfolioRank": None,
        "PortfolioStatus": "PENDING",
        "PortfolioReason": "",
        "SuggestedShares": 0,
        "SuggestedLots": 0,
        "SuggestedCapital": 0.0,
        "SuggestedMaxLoss": 0.0,
        "AllocatedShares": 0,
        "AllocatedLots": 0,
        "AllocatedCapital": 0.0,
        "AllocatedMaxLoss": 0.0,
        "AllocatedPotentialProfit": 0.0,
        "PortfolioAllocation": 0.0,
        "PortfolioRiskPercent": 0.0,
        "PortfolioRemainingCash": 0.0,

        # =====================================
        # SOURCE ENGINE DATA
        # =====================================
        "_engine": {
            "trend": dict(trend_data),
            "momentum": dict(momentum_data),
            "volume": dict(volume_data),
            "volatility": dict(volatility_data),
            "risk": dict(risk_data),
        },
    }

    result["analysis"] = {
        "summary": summary,
        "reasons": analysis_reasons,
        "warnings": analysis_warnings,
    }

    return sync_result_structure(result)


def sync_result_structure(result):
    """
    Selaraskan medan rata dengan struktur nested.

    Engine lama mengubah alias rata seperti FinalScore,
    InstitutionBonus dan CapitalUsed. Selepas setiap engine,
    fungsi ini memastikan struktur nested menerima nilai terkini.
    """

    if result is None or not isinstance(result, dict):
        result = {}

    identity = result.get("identity")
    if not isinstance(identity, dict):
        identity = {}

    score = result.get("score")
    if not isinstance(score, dict):
        score = {}

    confidence = result.get("confidence")
    if not isinstance(confidence, dict):
        confidence = {}

    market = result.get("market")
    if not isinstance(market, dict):
        market = {}

    trade = result.get("trade")
    if not isinstance(trade, dict):
        trade = {}

    position = result.get("position")
    if not isinstance(position, dict):
        position = {}

    analysis = result.get("analysis")
    if not isinstance(analysis, dict):
        analysis = {}

    portfolio = result.get("portfolio")
    if not isinstance(portfolio, dict):
        portfolio = {}

    # =====================================
    # IDENTITY
    # =====================================
    code = _safe_text(
        result.get("Code", identity.get("code", ""))
    )
    price = _safe_float(
        result.get("Price", identity.get("price", 0))
    )

    identity.update({
        "code": code,
        "price": price,
    })

    result["Code"] = code
    result["Price"] = round(price, 2)

    # =====================================
    # SCORE
    # =====================================
    raw = _safe_float(
        result.get(
            "RawScore",
            result.get(
                "Score",
                score.get("raw", 0)
            )
        )
    )

    quality_penalty = _safe_float(
        result.get(
            "QualityPenalty",
            score.get("quality_penalty", 0)
        )
    )

    tradeable = _safe_float(
        result.get(
            "TradeableScore",
            score.get(
                "tradeable",
                max(raw - quality_penalty, 0)
            )
        )
    )

    institution_bonus = _safe_float(
        result.get(
            "InstitutionBonus",
            score.get("institution_bonus", 0)
        )
    )

    regime_bonus = _safe_float(
        result.get(
            "RegimeBonus",
            score.get("regime_bonus", 0)
        )
    )

    regime_penalty = _safe_float(
        result.get(
            "RegimePenalty",
            score.get("regime_penalty", 0)
        )
    )

    final_score = _safe_float(
        result.get(
            "FinalScore",
            score.get(
                "final",
                tradeable
                + institution_bonus
                + regime_bonus
                - regime_penalty
            )
        )
    )

    grade = _safe_text(
        result.get(
            "Grade",
            score.get("grade", _grade_from_score(final_score))
        )
    )

    score.update({
        "raw": raw,
        "quality_penalty": quality_penalty,
        "tradeable": tradeable,
        "institution_bonus": institution_bonus,
        "regime_bonus": regime_bonus,
        "regime_penalty": regime_penalty,
        "final": final_score,
        "grade": grade,
    })

    result["RawScore"] = round(raw, 2)
    result["Score"] = round(raw, 2)
    result["QualityPenalty"] = round(quality_penalty, 2)
    result["TradeableScore"] = round(tradeable, 2)
    result["InstitutionBonus"] = round(institution_bonus, 2)
    result["RegimeBonus"] = round(regime_bonus, 2)
    result["RegimePenalty"] = round(regime_penalty, 2)
    result["FinalScore"] = round(final_score, 2)
    result["Grade"] = grade

    # =====================================
    # CONFIDENCE
    # =====================================
    confidence_value = _safe_float(
        result.get(
            "Confidence",
            confidence.get("value", 0)
        )
    )

    confidence_level = _safe_text(
        result.get(
            "ConfLevel",
            confidence.get("level", "UNKNOWN")
        )
    )

    confidence.update({
        "value": confidence_value,
        "level": confidence_level,
    })

    result["Confidence"] = round(confidence_value, 2)
    result["ConfLevel"] = confidence_level

    # =====================================
    # MARKET
    # =====================================
    trend = _safe_text(
        result.get(
            "Trend",
            market.get("trend", "UNKNOWN")
        )
    )

    volume = _safe_text(
        result.get(
            "Volume",
            market.get("volume", "UNKNOWN")
        )
    )

    smart_money = _safe_text(
        result.get(
            "SmartMoney",
            market.get("smart_money", "NONE")
        )
    )

    regime = _safe_text(
        result.get(
            "MarketRegime",
            market.get("regime", "UNKNOWN")
        )
    )

    regime_score = _safe_float(
        result.get(
            "RegimeScore",
            market.get("regime_score", 0)
        )
    )

    market.update({
        "trend": trend,
        "volume": volume,
        "smart_money": smart_money,
        "regime": regime,
        "regime_score": regime_score,
    })

    result["Trend"] = trend
    result["Volume"] = volume
    result["SmartMoney"] = smart_money
    result["MarketRegime"] = regime
    result["RegimeScore"] = round(regime_score, 2)

    # =====================================
    # TRADE
    # =====================================
    signal = _safe_text(
        result.get(
            "Signal",
            trade.get("signal", "UNKNOWN")
        )
    )

    decision_signal = _safe_text(
        result.get(
            "DecisionSignal",
            trade.get("decision_signal", signal)
        )
    )

    rating = _safe_text(
        result.get(
            "Rating",
            trade.get("rating", "UNKNOWN")
        )
    )

    entry = _safe_float(
        result.get(
            "Entry",
            trade.get("entry", price)
        )
    )

    stop_loss = _safe_float(
        result.get(
            "StopLoss",
            trade.get("stop_loss", 0)
        )
    )

    target = _safe_float(
        result.get(
            "Target",
            trade.get("target", 0)
        )
    )

    rr = _safe_float(
        result.get(
            "RR",
            trade.get("risk_reward", 0)
        )
    )

    trade.update({
        "signal": signal,
        "decision_signal": decision_signal,
        "rating": rating,
        "entry": entry,
        "stop_loss": stop_loss,
        "target": target,
        "risk_reward": rr,
    })

    result["Signal"] = signal
    result["DecisionSignal"] = decision_signal
    result["Rating"] = rating
    result["Entry"] = round(entry, 4)
    result["StopLoss"] = round(stop_loss, 4)
    result["Target"] = round(target, 4)
    result["RR"] = round(rr, 2)

    # =====================================
    # POSITION
    # =====================================
    position_map = {
        "account_capital": ("AccountCapital", 0.0, _safe_float),
        "risk_percent": ("RiskPercent", 0.0, _safe_float),
        "risk_capital": ("RiskCapital", 0.0, _safe_float),
        "risk_per_share": ("RiskPerShare", 0.0, _safe_float),
        "shares": ("Shares", 0, _safe_int),
        "lots": ("Lots", 0, _safe_int),
        "capital_used": ("CapitalUsed", 0.0, _safe_float),
        "remaining_capital": ("RemainingCapital", 0.0, _safe_float),
        "allocation_percent": ("Allocation", 0.0, _safe_float),
        "actual_risk_percent": ("ActualRiskPercent", 0.0, _safe_float),
        "max_loss": ("MaxLoss", 0.0, _safe_float),
        "potential_profit": ("PotentialProfit", 0.0, _safe_float),
    }

    for nested_key, (flat_key, default, converter) in position_map.items():
        value = converter(
            result.get(
                flat_key,
                position.get(nested_key, default)
            ),
            default
        )
        position[nested_key] = value
        result[flat_key] = value

    position["status"] = _safe_text(
        result.get(
            "PositionStatus",
            position.get("status", "PENDING")
        )
    )

    position["rating"] = _safe_text(
        result.get(
            "PositionRating",
            position.get("rating", "NONE")
        )
    )

    result["PositionStatus"] = position["status"]
    result["PositionRating"] = position["rating"]
    result["Capital"] = _safe_float(
        result.get("Capital", position["capital_used"])
    )

    # =====================================
    # ANALYSIS
    # =====================================
    summary = _safe_text(
        result.get(
            "Summary",
            analysis.get("summary", "")
        )
    )

    reasons = _safe_list(
        analysis.get(
            "reasons",
            result.get("Reason", [])
        )
    )

    warnings = _safe_list(
        analysis.get(
            "warnings",
            result.get("Warning", [])
        )
    )

    analysis.update({
        "summary": summary,
        "reasons": reasons,
        "warnings": warnings,
    })

    result["Summary"] = summary
    result["Reason"] = reasons
    result["Warning"] = warnings

    # =====================================
    # PORTFOLIO
    # =====================================
    portfolio_map = {
        "eligible": ("PortfolioEligible", False, bool),
        "rank": ("PortfolioRank", None, lambda value: value),
        "status": ("PortfolioStatus", "PENDING", _safe_text),
        "reason": ("PortfolioReason", "", _safe_text),
        "suggested_shares": ("SuggestedShares", 0, _safe_int),
        "suggested_lots": ("SuggestedLots", 0, _safe_int),
        "suggested_capital": ("SuggestedCapital", 0.0, _safe_float),
        "suggested_max_loss": ("SuggestedMaxLoss", 0.0, _safe_float),
        "allocated_shares": ("AllocatedShares", 0, _safe_int),
        "allocated_lots": ("AllocatedLots", 0, _safe_int),
        "allocated_capital": ("AllocatedCapital", 0.0, _safe_float),
        "allocated_max_loss": ("AllocatedMaxLoss", 0.0, _safe_float),
        "allocated_potential_profit": (
            "AllocatedPotentialProfit",
            0.0,
            _safe_float
        ),
        "allocation_percent": ("PortfolioAllocation", 0.0, _safe_float),
        "risk_percent": ("PortfolioRiskPercent", 0.0, _safe_float),
        "remaining_cash_after": (
            "PortfolioRemainingCash",
            0.0,
            _safe_float
        ),
    }

    for nested_key, (flat_key, default, converter) in portfolio_map.items():
        raw_value = result.get(
            flat_key,
            portfolio.get(nested_key, default)
        )

        try:
            value = converter(raw_value)
        except TypeError:
            value = converter(raw_value, default)

        portfolio[nested_key] = value
        result[flat_key] = value

    result["identity"] = identity
    result["score"] = score
    result["confidence"] = confidence
    result["market"] = market
    result["trade"] = trade
    result["position"] = position
    result["analysis"] = analysis
    result["portfolio"] = portfolio

    return result