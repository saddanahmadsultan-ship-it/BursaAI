"""
BursaAI v6.0 Sprint 6B Paper Trading test.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Framework.context import AnalysisContext
from Framework.infrastructure import (
    build_infrastructure,
)
from Trading.paper_order import (
    OrderSide,
    OrderStatus,
    PaperOrder,
)
from Trading.paper_services import (
    register_paper_trading,
)


def commission(order):
    return 5.0


def build_context():
    context = AnalysisContext(
        symbol="1155.KL"
    )

    context.analysis.identity.price = 10.0
    context.analysis.trade.entry = 10.0

    context.analysis.portfolio.status = "ALLOCATED"
    context.analysis.portfolio.allocated_shares = 1000
    context.analysis.portfolio.allocated_capital = 10000

    return context


def main():
    infrastructure = build_infrastructure()
    events = []

    infrastructure.events.subscribe(
        "PaperOrderUpdated",
        lambda event: events.append(event),
    )

    portfolio = register_paper_trading(
        infrastructure.services,
        starting_capital=100000,
        commission_function=commission,
        slippage_percent=0.1,
    )

    context = build_context()

    result = portfolio.open_allocated_positions(
        [context]
    )

    account = infrastructure.services.resolve(
        "paper_account"
    )

    engine = infrastructure.services.resolve(
        "paper_execution_engine"
    )

    assert len(result["orders"]) == 1
    assert result["orders"][0].status == OrderStatus.FILLED

    position = account.positions["1155.KL"]

    assert position.shares == 1000
    assert position.average_price == 10.01
    assert round(account.cash, 2) == 89985.00
    assert account.total_commission == 5.0

    portfolio.update_prices(
        {
            "1155.KL": 10.50,
        }
    )

    assert position.market_price == 10.50
    assert position.unrealized_pnl == 490.0

    sell_order = portfolio.close_position(
        "1155.KL",
        10.60,
    )

    assert sell_order is not None
    assert sell_order.status == OrderStatus.FILLED
    assert position.shares == 0
    assert account.realized_pnl > 0
    assert len(engine.orders) == 2
    assert len(events) == 2

    rejected = engine.execute(
        PaperOrder(
            symbol="1023.KL",
            side=OrderSide.BUY,
            shares=999999,
            price=10.0,
        )
    )

    assert rejected.status == OrderStatus.REJECTED
    assert rejected.reason == "INSUFFICIENT CASH"

    print("=" * 88)
    print("BURSAAI v6.0 SPRINT 6B TEST")
    print("=" * 88)
    print("Paper Account            : OK")
    print("Paper Order              : OK")
    print("Paper Position           : OK")
    print("Paper Execution          : OK")
    print("Commission Handling      : OK")
    print("Slippage Handling        : OK")
    print("Portfolio Order Creation : OK")
    print("Profit / Loss            : OK")
    print("Order Rejection          : OK")
    print("Paper Trading Event      : OK")
    print("=" * 88)
    print("SPRINT 6B PAPER TRADING ENGINE OK")


if __name__ == "__main__":
    main()
