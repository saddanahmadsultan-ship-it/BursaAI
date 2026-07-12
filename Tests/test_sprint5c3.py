"""
BursaAI v6.0 Sprint 5C.3 Portfolio Allocator Adapter test.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Adapters.portfolio_allocator_adapter import (
    PortfolioAllocatorAdapter,
)
from Framework.context import AnalysisContext
from Framework.infrastructure import build_infrastructure


def build_context(
    symbol,
    score,
    confidence,
    signal,
    entry,
    stop_loss,
    target,
    rr,
    shares,
    lots,
    capital,
    max_loss,
    profit,
):
    context = AnalysisContext(symbol=symbol)

    analysis = context.analysis
    analysis.identity.code = symbol
    analysis.identity.price = entry
    analysis.score.final = score
    analysis.confidence = confidence
    analysis.trade.signal = signal
    analysis.trade.entry = entry
    analysis.trade.stop_loss = stop_loss
    analysis.trade.target = target
    analysis.trade.risk_reward = rr

    analysis.position.account_capital = 100000
    analysis.position.shares = shares
    analysis.position.lots = lots
    analysis.position.capital_used = capital
    analysis.position.max_loss = max_loss
    analysis.position.potential_profit = profit
    analysis.position.status = "READY"

    return context


def fake_allocate_portfolio(results):
    output = []

    first = dict(results[0])
    first["portfolio"] = {
        "eligible": True,
        "rank": 1,
        "status": "ALLOCATED",
        "reason": "PORTFOLIO APPROVED",
        "suggested_shares": 2000,
        "suggested_lots": 20,
        "suggested_capital": 20800,
        "suggested_max_loss": 800,
        "allocated_shares": 2000,
        "allocated_lots": 20,
        "allocated_capital": 20800,
        "allocated_max_loss": 800,
        "allocated_potential_profit": 1600,
        "allocation_percent": 20.8,
        "risk_percent": 0.8,
        "remaining_cash_after": 79200,
    }
    output.append(first)

    second = dict(results[1])
    second["portfolio"] = {
        "eligible": False,
        "rank": None,
        "status": "SKIP",
        "reason": "LOW FINAL SCORE",
        "suggested_shares": 1000,
        "suggested_lots": 10,
        "suggested_capital": 7650,
        "suggested_max_loss": 400,
        "allocated_shares": 0,
        "allocated_lots": 0,
        "allocated_capital": 0,
        "allocated_max_loss": 0,
        "allocated_potential_profit": 0,
        "allocation_percent": 0,
        "risk_percent": 0,
        "remaining_cash_after": 79200,
    }
    output.append(second)

    summary = {
        "account_capital": 100000,
        "cash_reserve": 10000,
        "deployable_capital": 90000,
        "capital_allocated": 20800,
        "remaining_cash": 79200,
        "portfolio_risk_amount": 800,
        "portfolio_risk_pct": 0.8,
        "maximum_portfolio_risk_pct": 5.0,
        "active_positions": 1,
        "maximum_active_positions": 5,
        "exposure_pct": 20.8,
        "cash_pct": 79.2,
        "average_final_score": 88,
        "average_confidence": 92,
        "status": "PARTIALLY ALLOCATED",
    }

    return {
        "results": output,
        "positions": output,
        "summary": summary,
    }


def main():
    infrastructure = build_infrastructure()
    events = []

    infrastructure.events.subscribe(
        "PortfolioAllocated",
        lambda event: events.append(event),
    )

    strong = build_context(
        "1155.KL", 88, 92, "STRONG BUY",
        10.4, 10.0, 11.2, 2.0,
        2000, 20, 20800, 800, 1600,
    )

    weak = build_context(
        "1023.KL", 60, 55, "WATCH",
        7.65, 7.25, 8.45, 2.0,
        1000, 10, 7650, 400, 800,
    )

    adapter = PortfolioAllocatorAdapter(
        allocator_function=fake_allocate_portfolio,
        services=infrastructure.services,
    )

    result = adapter.allocate([weak, strong])

    assert len(result["contexts"]) == 2
    assert result["summary"]["capital_allocated"] == 20800

    assert strong.analysis.portfolio.eligible is True
    assert strong.analysis.portfolio.rank == 1
    assert strong.analysis.portfolio.status == "ALLOCATED"
    assert strong.analysis.portfolio.allocated_shares == 2000
    assert strong.analysis.portfolio.allocated_lots == 20
    assert strong.analysis.portfolio.allocated_capital == 20800
    assert strong.analysis.portfolio.allocated_max_loss == 800
    assert strong.analysis.portfolio.risk_percent == 0.8
    assert strong.analysis.portfolio.remaining_cash_after == 79200

    assert weak.analysis.portfolio.eligible is False
    assert weak.analysis.portfolio.status == "SKIP"
    assert weak.analysis.portfolio.reason == "LOW FINAL SCORE"

    assert len(events) == 1
    assert events[0].payload["active_positions"] == 1
    assert events[0].payload["status"] == "PARTIALLY ALLOCATED"

    print("=" * 88)
    print("BURSAAI v6.0 SPRINT 5C.3 TEST")
    print("=" * 88)
    print("Batch Portfolio Adapter    : OK")
    print("Ranking Before Allocation  : OK")
    print("Portfolio Model Sync       : OK")
    print("Allocated Position Sync    : OK")
    print("Skipped Position Sync      : OK")
    print("Portfolio Summary Sync     : OK")
    print("Portfolio Event            : OK")
    print("=" * 88)
    print("SPRINT 5C.3 PORTFOLIO ALLOCATOR ADAPTER OK")


if __name__ == "__main__":
    main()
