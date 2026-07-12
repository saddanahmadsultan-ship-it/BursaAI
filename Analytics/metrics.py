"""
=========================================================
BursaAI Performance Metric Helpers
Version : 6.0 Sprint 6E
=========================================================
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Dict, Iterable, List, Tuple


def build_equity_curve(
    pnls: Iterable[float],
    starting_capital: float,
) -> List[float]:
    equity = float(starting_capital)
    curve = [round(equity, 2)]

    for pnl in pnls:
        equity += float(pnl)
        curve.append(round(equity, 2))

    return curve


def maximum_drawdown(
    equity_curve: List[float],
) -> Tuple[float, float]:
    if not equity_curve:
        return 0.0, 0.0

    peak = equity_curve[0]
    max_amount = 0.0
    max_percent = 0.0

    for equity in equity_curve:
        if equity > peak:
            peak = equity

        drawdown = peak - equity

        if drawdown > max_amount:
            max_amount = drawdown

        if peak > 0:
            drawdown_percent = (
                drawdown / peak * 100
            )

            if drawdown_percent > max_percent:
                max_percent = drawdown_percent

    return (
        round(max_amount, 2),
        round(max_percent, 4),
    )


def maximum_streaks(
    pnls: Iterable[float],
) -> Tuple[int, int]:
    max_wins = 0
    max_losses = 0
    wins = 0
    losses = 0

    for pnl in pnls:
        if pnl > 0:
            wins += 1
            losses = 0
        elif pnl < 0:
            losses += 1
            wins = 0
        else:
            wins = 0
            losses = 0

        max_wins = max(max_wins, wins)
        max_losses = max(max_losses, losses)

    return max_wins, max_losses


def calculate_monthly_returns(
    records: Iterable[Dict],
) -> Dict[str, float]:
    totals = defaultdict(float)

    for record in records:
        created_at = str(
            record.get("created_at", "")
        )

        try:
            month = datetime.fromisoformat(
                created_at.replace("Z", "+00:00")
            ).strftime("%Y-%m")
        except ValueError:
            month = "UNKNOWN"

        totals[month] += float(
            record.get("pnl", 0) or 0
        )

    return {
        key: round(value, 2)
        for key, value in sorted(
            totals.items()
        )
    }
