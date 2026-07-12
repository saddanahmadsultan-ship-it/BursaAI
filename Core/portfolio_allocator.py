"""
=========================================================
BursaAI Portfolio Allocation Engine
Version : 5.0 Professional
Batch   : 3D Stable
=========================================================
"""

import math
from copy import deepcopy

from Core.portfolio_config import get_portfolio_config


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value, default=0):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _round_money(value):
    return round(_safe_float(value), 2)


def _normalise_signal(value):
    signal = str(value or "").upper().strip()

    for token in ("🟢", "🟡", "🟠", "🔴", "⚪", "✅", "❌"):
        signal = signal.replace(token, "")

    return " ".join(signal.split())


def _zero_portfolio(reason, status="SKIP"):
    return {
        "eligible": False,
        "rank": None,
        "status": status,
        "reason": reason,
        "suggested_shares": 0,
        "suggested_lots": 0,
        "suggested_capital": 0.0,
        "suggested_max_loss": 0.0,
        "allocated_shares": 0,
        "allocated_lots": 0,
        "allocated_capital": 0.0,
        "allocated_max_loss": 0.0,
        "allocated_potential_profit": 0.0,
        "allocation_percent": 0.0,
        "risk_percent": 0.0,
        "remaining_cash_after": 0.0,
    }


def _sync_portfolio_aliases(result):
    portfolio = result.get("portfolio", {})

    result["PortfolioEligible"] = portfolio.get("eligible", False)
    result["PortfolioRank"] = portfolio.get("rank")
    result["PortfolioStatus"] = portfolio.get("status", "SKIP")
    result["PortfolioReason"] = portfolio.get("reason", "")
    result["SuggestedShares"] = portfolio.get("suggested_shares", 0)
    result["SuggestedLots"] = portfolio.get("suggested_lots", 0)
    result["SuggestedCapital"] = portfolio.get("suggested_capital", 0.0)
    result["SuggestedMaxLoss"] = portfolio.get("suggested_max_loss", 0.0)
    result["AllocatedShares"] = portfolio.get("allocated_shares", 0)
    result["AllocatedLots"] = portfolio.get("allocated_lots", 0)
    result["AllocatedCapital"] = portfolio.get("allocated_capital", 0.0)
    result["AllocatedMaxLoss"] = portfolio.get("allocated_max_loss", 0.0)
    result["AllocatedPotentialProfit"] = portfolio.get(
        "allocated_potential_profit", 0.0
    )
    result["PortfolioAllocation"] = portfolio.get("allocation_percent", 0.0)
    result["PortfolioRiskPercent"] = portfolio.get("risk_percent", 0.0)
    result["PortfolioRemainingCash"] = portfolio.get(
        "remaining_cash_after", 0.0
    )

    return result


def _candidate_data(result):
    identity = result.get("identity", {})
    score = result.get("score", {})
    confidence = result.get("confidence", {})
    trade = result.get("trade", {})
    position = result.get("position", {})

    return {
        "code": identity.get("code", result.get("Code", "")),
        "final_score": _safe_float(
            score.get("final", result.get("FinalScore", 0))
        ),
        "confidence": _safe_float(
            confidence.get("value", result.get("Confidence", 0))
        ),
        "signal": _normalise_signal(
            trade.get("signal", result.get("Signal", "UNKNOWN"))
        ),
        "entry": _safe_float(trade.get("entry", result.get("Entry", 0))),
        "stop_loss": _safe_float(
            trade.get("stop_loss", result.get("StopLoss", 0))
        ),
        "target": _safe_float(trade.get("target", result.get("Target", 0))),
        "rr": _safe_float(
            trade.get("risk_reward", result.get("RR", 0))
        ),
        "shares": _safe_int(position.get("shares", result.get("Shares", 0))),
        "lots": _safe_int(position.get("lots", result.get("Lots", 0))),
        "capital": _safe_float(
            position.get("capital_used", result.get("CapitalUsed", 0))
        ),
        "max_loss": _safe_float(
            position.get("max_loss", result.get("MaxLoss", 0))
        ),
        "potential_profit": _safe_float(
            position.get(
                "potential_profit", result.get("PotentialProfit", 0)
            )
        ),
        "position_status": str(
            position.get("status", result.get("PositionStatus", "UNKNOWN"))
        ),
    }


def allocate_portfolio(results):
    """Allocate one real account across ranked position suggestions."""

    config = get_portfolio_config()

    account_capital = _safe_float(config.get("capital", 0))
    max_risk_pct = _safe_float(config.get("max_portfolio_risk_percent", 0))
    reserve_pct = _safe_float(config.get("cash_reserve_percent", 0))
    max_positions = _safe_int(config.get("max_active_positions", 0))
    lot_size = max(_safe_int(config.get("lot_size", 100), 100), 1)
    min_score = _safe_float(config.get("minimum_final_score", 0))
    min_confidence = _safe_float(config.get("minimum_confidence", 0))
    min_rr = _safe_float(config.get("minimum_risk_reward", 0))
    allowed_signals = {
        _normalise_signal(signal)
        for signal in config.get("allowed_signals", set())
    }

    reserve_amount = account_capital * reserve_pct / 100.0
    deployable_capital = max(account_capital - reserve_amount, 0.0)
    max_risk_amount = account_capital * max_risk_pct / 100.0

    allocated_capital = 0.0
    allocated_risk = 0.0
    active_positions = 0

    output = deepcopy(results or [])

    for result in output:
        data = _candidate_data(result)

        portfolio = _zero_portfolio("NOT EVALUATED")
        portfolio.update(
            {
                "suggested_shares": data["shares"],
                "suggested_lots": data["lots"],
                "suggested_capital": _round_money(data["capital"]),
                "suggested_max_loss": _round_money(data["max_loss"]),
            }
        )

        reason = None

        if account_capital <= 0:
            reason = "INVALID ACCOUNT CAPITAL"
        elif data["signal"] not in allowed_signals:
            reason = "SIGNAL NOT ELIGIBLE"
        elif data["final_score"] < min_score:
            reason = "LOW FINAL SCORE"
        elif data["confidence"] < min_confidence:
            reason = "LOW CONFIDENCE"
        elif data["rr"] < min_rr:
            reason = "POOR RISK REWARD"
        elif data["entry"] <= 0:
            reason = "INVALID ENTRY"
        elif data["stop_loss"] <= 0 or data["stop_loss"] >= data["entry"]:
            reason = "INVALID STOP LOSS"
        elif data["shares"] <= 0 or data["capital"] <= 0:
            reason = "NO POSITION SUGGESTION"
        elif "SKIP" in data["position_status"].upper():
            reason = data["position_status"].upper()

        if reason:
            portfolio["reason"] = reason
            portfolio["remaining_cash_after"] = _round_money(
                account_capital - allocated_capital
            )
            result["portfolio"] = portfolio
            _sync_portfolio_aliases(result)
            continue

        if active_positions >= max_positions:
            portfolio["status"] = "SKIP"
            portfolio["reason"] = "MAX ACTIVE POSITIONS REACHED"
            portfolio["remaining_cash_after"] = _round_money(
                account_capital - allocated_capital
            )
            result["portfolio"] = portfolio
            _sync_portfolio_aliases(result)
            continue

        remaining_deployable = max(deployable_capital - allocated_capital, 0.0)
        remaining_risk = max(max_risk_amount - allocated_risk, 0.0)

        if remaining_deployable < data["entry"] * lot_size:
            portfolio["status"] = "NO CAPITAL"
            portfolio["reason"] = "INSUFFICIENT DEPLOYABLE CAPITAL"
            portfolio["remaining_cash_after"] = _round_money(
                account_capital - allocated_capital
            )
            result["portfolio"] = portfolio
            _sync_portfolio_aliases(result)
            continue

        risk_per_share = abs(data["entry"] - data["stop_loss"])

        shares_by_capital = math.floor(remaining_deployable / data["entry"])
        shares_by_risk = math.floor(remaining_risk / risk_per_share)

        allocated_shares = min(
            data["shares"],
            shares_by_capital,
            shares_by_risk,
        )

        allocated_lots = math.floor(allocated_shares / lot_size)
        allocated_shares = allocated_lots * lot_size

        if allocated_shares <= 0:
            portfolio["status"] = "NO CAPITAL" if remaining_deployable <= 0 else "SKIP"
            portfolio["reason"] = (
                "PORTFOLIO RISK LIMIT REACHED"
                if remaining_risk < risk_per_share * lot_size
                else "ALLOCATION BELOW ONE BOARD LOT"
            )
            portfolio["remaining_cash_after"] = _round_money(
                account_capital - allocated_capital
            )
            result["portfolio"] = portfolio
            _sync_portfolio_aliases(result)
            continue

        final_capital = allocated_shares * data["entry"]
        final_loss = allocated_shares * risk_per_share
        final_profit = (
            allocated_shares * (data["target"] - data["entry"])
            if data["target"] > data["entry"]
            else 0.0
        )

        allocated_capital += final_capital
        allocated_risk += final_loss
        active_positions += 1

        status = (
            "ALLOCATED"
            if allocated_shares == data["shares"]
            else "REDUCED"
        )

        portfolio.update(
            {
                "eligible": True,
                "rank": active_positions,
                "status": status,
                "reason": "PORTFOLIO APPROVED",
                "allocated_shares": int(allocated_shares),
                "allocated_lots": int(allocated_lots),
                "allocated_capital": _round_money(final_capital),
                "allocated_max_loss": _round_money(final_loss),
                "allocated_potential_profit": _round_money(final_profit),
                "allocation_percent": round(
                    final_capital / account_capital * 100.0, 2
                ),
                "risk_percent": round(
                    final_loss / account_capital * 100.0, 2
                ),
                "remaining_cash_after": _round_money(
                    account_capital - allocated_capital
                ),
            }
        )

        result["portfolio"] = portfolio
        _sync_portfolio_aliases(result)

    remaining_cash = max(account_capital - allocated_capital, 0.0)

    active = [
        item for item in output
        if item.get("portfolio", {}).get("status") in {"ALLOCATED", "REDUCED"}
    ]

    avg_score = (
        sum(_candidate_data(item)["final_score"] for item in active) / len(active)
        if active else 0.0
    )
    avg_confidence = (
        sum(_candidate_data(item)["confidence"] for item in active) / len(active)
        if active else 0.0
    )

    summary = {
        "account_capital": _round_money(account_capital),
        "cash_reserve": _round_money(reserve_amount),
        "deployable_capital": _round_money(deployable_capital),
        "capital_allocated": _round_money(allocated_capital),
        "remaining_cash": _round_money(remaining_cash),
        "portfolio_risk_amount": _round_money(allocated_risk),
        "portfolio_risk_pct": round(
            allocated_risk / account_capital * 100.0 if account_capital else 0.0,
            2,
        ),
        "maximum_portfolio_risk_pct": round(max_risk_pct, 2),
        "active_positions": active_positions,
        "maximum_active_positions": max_positions,
        "exposure_pct": round(
            allocated_capital / account_capital * 100.0 if account_capital else 0.0,
            2,
        ),
        "cash_pct": round(
            remaining_cash / account_capital * 100.0 if account_capital else 0.0,
            2,
        ),
        "average_final_score": round(avg_score, 2),
        "average_confidence": round(avg_confidence, 2),
        "status": (
            "NO ACTIVE POSITIONS"
            if active_positions == 0
            else "RISK LIMIT NEARLY FULL"
            if allocated_risk >= max_risk_amount * 0.95
            else "FULLY ALLOCATED"
            if allocated_capital >= deployable_capital * 0.95
            else "PARTIALLY ALLOCATED"
        ),
    }

    return {
        "results": output,
        "positions": output,
        "summary": summary,
    }


def print_portfolio_positions(portfolio_data):
    results = portfolio_data.get("results", [])

    print("\n")
    print("=" * 132)
    print("FINAL PORTFOLIO ALLOCATION")
    print("=" * 132)
    print(
        f"{'Rank':<6}{'Code':<11}{'Status':<13}{'Signal':<12}"
        f"{'Shares':>11}{'Lots':>8}{'Capital':>15}{'Risk':>13}"
        f"{'Alloc%':>10}{'Risk%':>9}{'Cash After':>16}"
    )
    print("-" * 132)

    shown = False

    for item in results:
        portfolio = item.get("portfolio", {})
        status = portfolio.get("status", "SKIP")

        if status not in {"ALLOCATED", "REDUCED", "NO CAPITAL"}:
            continue

        data = _candidate_data(item)
        shown = True

        print(
            f"{str(portfolio.get('rank') or '-'): <6}"
            f"{data['code']:<11}"
            f"{status:<13}"
            f"{data['signal']:<12}"
            f"{portfolio.get('allocated_shares', 0):>11,}"
            f"{portfolio.get('allocated_lots', 0):>8,}"
            f"{portfolio.get('allocated_capital', 0):>15,.2f}"
            f"{portfolio.get('allocated_max_loss', 0):>13,.2f}"
            f"{portfolio.get('allocation_percent', 0):>10.2f}"
            f"{portfolio.get('risk_percent', 0):>9.2f}"
            f"{portfolio.get('remaining_cash_after', 0):>16,.2f}"
        )

    if not shown:
        print("Tiada posisi portfolio yang diperuntukkan.")

    print("=" * 132)


def print_portfolio_summary(portfolio_data):
    summary = portfolio_data.get("summary", {})

    print("\n")
    print("=" * 72)
    print("PORTFOLIO SUMMARY")
    print("=" * 72)
    print(f"Account Capital        : RM{summary.get('account_capital', 0):,.2f}")
    print(f"Deployable Capital     : RM{summary.get('deployable_capital', 0):,.2f}")
    print(f"Cash Reserve           : RM{summary.get('cash_reserve', 0):,.2f}")
    print(f"Capital Allocated      : RM{summary.get('capital_allocated', 0):,.2f}")
    print(f"Remaining Cash         : RM{summary.get('remaining_cash', 0):,.2f}")
    print(f"Portfolio Risk         : {summary.get('portfolio_risk_pct', 0):.2f}%")
    print(
        "Maximum Portfolio Risk : "
        f"{summary.get('maximum_portfolio_risk_pct', 0):.2f}%"
    )
    print(f"Active Positions       : {summary.get('active_positions', 0)}")
    print(f"Maximum Positions      : {summary.get('maximum_active_positions', 0)}")
    print(f"Portfolio Exposure     : {summary.get('exposure_pct', 0):.2f}%")
    print(f"Cash Percentage        : {summary.get('cash_pct', 0):.2f}%")
    print(f"Average Final Score    : {summary.get('average_final_score', 0):.2f}")
    print(f"Average Confidence     : {summary.get('average_confidence', 0):.2f}%")
    print(f"Portfolio Status       : {summary.get('status', 'UNKNOWN')}")
    print("=" * 72)