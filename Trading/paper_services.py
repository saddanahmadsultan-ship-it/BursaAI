"""
=========================================================
BursaAI Paper Trading Service Registration
Version : 6.0 Sprint 6B
=========================================================
"""

from __future__ import annotations

from typing import Callable, Optional

from Framework.service_container import ServiceContainer
from Trading.paper_account import PaperAccount
from Trading.paper_execution import PaperExecutionEngine
from Trading.paper_order import PaperOrder
from Trading.paper_portfolio import PaperPortfolio


def register_paper_trading(
    services: ServiceContainer,
    *,
    starting_capital: float = 100000.0,
    commission_function: Optional[
        Callable[[PaperOrder], float]
    ] = None,
    slippage_percent: float = 0.0,
) -> PaperPortfolio:
    account = PaperAccount(
        starting_capital=starting_capital,
        cash=starting_capital,
    )

    engine = PaperExecutionEngine(
        account=account,
        commission_function=commission_function,
        slippage_percent=slippage_percent,
        services=services,
    )

    portfolio = PaperPortfolio(
        account=account,
        execution_engine=engine,
    )

    services.register_instance(
        "paper_account",
        account,
        replace=True,
    )

    services.register_instance(
        "paper_execution_engine",
        engine,
        replace=True,
    )

    services.register_instance(
        "paper_portfolio",
        portfolio,
        replace=True,
    )

    return portfolio
