"""
=========================================================
BursaAI Notification Message Formatter
Version : 6.0 Sprint 6C
=========================================================
"""

from __future__ import annotations

from typing import Any, Dict

from Notifications.notification_message import (
    NotificationMessage,
)


def _money(value: Any) -> str:
    try:
        return f"RM{float(value):,.2f}"
    except (TypeError, ValueError):
        return "RM0.00"


def format_event_message(
    event_name: str,
    payload: Dict[str, Any],
) -> NotificationMessage:
    payload = payload or {}

    if event_name == "ExecutionStarted":
        symbols = payload.get("symbols", [])

        return NotificationMessage(
            title="🚀 BursaAI Execution Started",
            body=(
                f"Run ID: {payload.get('run_id', '-')}\n"
                f"Stocks: {len(symbols)}"
            ),
            level="INFO",
            event_name=event_name,
            metadata=payload,
        )

    if event_name == "ExecutionCompleted":
        portfolio = payload.get(
            "portfolio_summary",
            {},
        )

        return NotificationMessage(
            title="✅ BursaAI Execution Completed",
            body=(
                f"Successful: {payload.get('successful', 0)}\n"
                f"Failed: {payload.get('failed', 0)}\n"
                f"Average Score: {payload.get('average_score', 0):.2f}\n"
                f"Average Confidence: "
                f"{payload.get('average_confidence', 0):.2f}%\n"
                f"Capital Allocated: "
                f"{_money(portfolio.get('capital_allocated', 0))}\n"
                f"Remaining Cash: "
                f"{_money(portfolio.get('remaining_cash', 0))}"
            ),
            level="SUCCESS",
            event_name=event_name,
            metadata=payload,
        )

    if event_name == "PortfolioAllocated":
        return NotificationMessage(
            title="💼 Portfolio Allocated",
            body=(
                f"Capital: "
                f"{_money(payload.get('capital_allocated', 0))}\n"
                f"Cash: "
                f"{_money(payload.get('remaining_cash', 0))}\n"
                f"Portfolio Risk: "
                f"{float(payload.get('portfolio_risk_pct', 0)):.2f}%\n"
                f"Active Positions: "
                f"{payload.get('active_positions', 0)}\n"
                f"Status: {payload.get('status', 'UNKNOWN')}"
            ),
            level="INFO",
            event_name=event_name,
            metadata=payload,
        )

    if event_name == "PaperOrderUpdated":
        return NotificationMessage(
            title="🧾 Paper Order Update",
            body=(
                f"{payload.get('side', '-')}"
                f" {payload.get('symbol', '-')}\n"
                f"Status: {payload.get('status', '-')}\n"
                f"Shares: {payload.get('filled_shares', 0)}\n"
                f"Price: {payload.get('filled_price', 0)}\n"
                f"Cash: {_money(payload.get('cash', 0))}\n"
                f"Reason: {payload.get('reason', '-') or '-'}"
            ),
            level="INFO",
            event_name=event_name,
            metadata=payload,
        )

    if event_name == "DecisionCompleted":
        return NotificationMessage(
            title="📊 Trading Decision",
            body=(
                f"Symbol: {payload.get('symbol', '-')}\n"
                f"Recommendation: "
                f"{payload.get('recommendation', 'UNKNOWN')}\n"
                f"Rating: {payload.get('rating', '-')}\n"
                f"Quality: {payload.get('quality', 0)}\n"
                f"{payload.get('summary', '')}"
            ),
            level="INFO",
            event_name=event_name,
            metadata=payload,
        )

    if event_name == "ExecutionFailed":
        return NotificationMessage(
            title="❌ BursaAI Execution Failed",
            body=(
                f"Run ID: {payload.get('run_id', '-')}\n"
                f"Error: {payload.get('error', 'UNKNOWN')}"
            ),
            level="ERROR",
            event_name=event_name,
            metadata=payload,
        )

    return NotificationMessage(
        title=f"🔔 {event_name}",
        body=str(payload),
        level="INFO",
        event_name=event_name,
        metadata=payload,
    )
