"""
=========================================================
BursaAI Portfolio Allocator Adapter
Version : 6.0 Sprint 5C.3
=========================================================

IMPORTANT:
Portfolio allocation is a batch operation across multiple stocks.
It must run after all per-stock pipelines have completed.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Callable, Dict, Iterable, List, Optional

from Framework.context import AnalysisContext
from Framework.event_bus import EventBus
from Framework.exceptions import ValidationError
from Framework.legacy_bridge import LegacyBridge
from Framework.service_container import ServiceContainer


class PortfolioAllocatorAdapter:
    """
    Wrap:
        Core.portfolio_allocator.allocate_portfolio(results)

    Input:
        Iterable[AnalysisContext]

    Output:
        {
            "contexts": [...],
            "results": [...],
            "positions": [...],
            "summary": {...},
        }
    """

    NAME = "Portfolio Allocator Adapter"
    VERSION = "6.0"

    def __init__(
        self,
        allocator_function: Optional[Callable[[List[Dict]], Dict]] = None,
        services: Optional[ServiceContainer] = None,
        event_bus: Optional[EventBus] = None,
        bridge: Optional[LegacyBridge] = None,
    ):
        if allocator_function is None:
            from Core.portfolio_allocator import allocate_portfolio
            allocator_function = allocate_portfolio

        self.allocator_function = allocator_function
        self.services = services
        self.bridge = bridge or LegacyBridge()

        if event_bus is not None:
            self.event_bus = event_bus
        elif services is not None and services.contains("event_bus"):
            self.event_bus = services.resolve("event_bus")
        else:
            self.event_bus = None

    def _validate_contexts(
        self,
        contexts: Iterable[AnalysisContext],
    ) -> List[AnalysisContext]:
        items = list(contexts or [])

        if not items:
            raise ValidationError(
                "Portfolio allocation requires at least one AnalysisContext."
            )

        for item in items:
            if not isinstance(item, AnalysisContext):
                raise ValidationError(
                    "Portfolio allocation accepts AnalysisContext objects only."
                )

        return items

    def _sync_portfolio(
        self,
        context: AnalysisContext,
        result: Dict,
    ) -> None:
        portfolio = result.get("portfolio", {})

        if not isinstance(portfolio, dict):
            portfolio = {}

        model = context.analysis.portfolio

        model.eligible = bool(portfolio.get("eligible", False))
        model.rank = portfolio.get("rank")
        model.status = str(portfolio.get("status", "SKIP"))
        model.reason = str(portfolio.get("reason", ""))

        model.suggested_shares = self.bridge._safe_int(
            portfolio.get("suggested_shares", 0)
        )
        model.suggested_lots = self.bridge._safe_int(
            portfolio.get("suggested_lots", 0)
        )
        model.suggested_capital = self.bridge._safe_float(
            portfolio.get("suggested_capital", 0)
        )
        model.suggested_max_loss = self.bridge._safe_float(
            portfolio.get("suggested_max_loss", 0)
        )

        model.allocated_shares = self.bridge._safe_int(
            portfolio.get("allocated_shares", 0)
        )
        model.allocated_lots = self.bridge._safe_int(
            portfolio.get("allocated_lots", 0)
        )
        model.allocated_capital = self.bridge._safe_float(
            portfolio.get("allocated_capital", 0)
        )
        model.allocated_max_loss = self.bridge._safe_float(
            portfolio.get("allocated_max_loss", 0)
        )
        model.allocated_potential_profit = self.bridge._safe_float(
            portfolio.get("allocated_potential_profit", 0)
        )
        model.allocation_percent = self.bridge._safe_float(
            portfolio.get("allocation_percent", 0)
        )
        model.risk_percent = self.bridge._safe_float(
            portfolio.get("risk_percent", 0)
        )
        model.remaining_cash_after = self.bridge._safe_float(
            portfolio.get("remaining_cash_after", 0)
        )

        context.metadata["portfolio_data"] = deepcopy(result)
        context.analysis.extra["portfolio"] = deepcopy(portfolio)

    def allocate(
        self,
        contexts: Iterable[AnalysisContext],
    ) -> Dict:
        items = self._validate_contexts(contexts)

        ranked = sorted(
            items,
            key=lambda context: context.analysis.score.final,
            reverse=True,
        )

        legacy_results = [
            self.bridge.context_to_legacy(context)
            for context in ranked
        ]

        allocation = self.allocator_function(legacy_results)

        if not isinstance(allocation, dict):
            raise ValidationError(
                "Portfolio allocator output must be a dictionary."
            )

        results = allocation.get("results", [])

        if not isinstance(results, list):
            raise ValidationError(
                "Portfolio allocator output['results'] must be a list."
            )

        context_by_code = {
            context.analysis.identity.code: context
            for context in ranked
        }

        synchronized: List[AnalysisContext] = []

        for result in results:
            if not isinstance(result, dict):
                continue

            code = str(
                result.get(
                    "Code",
                    result.get("identity", {}).get("code", ""),
                )
            )

            context = context_by_code.get(code)

            if context is None:
                continue

            self._sync_portfolio(context, result)
            synchronized.append(context)

        summary = deepcopy(allocation.get("summary", {}))

        for context in synchronized:
            context.metadata["portfolio_summary"] = deepcopy(summary)

        output = {
            "contexts": synchronized,
            "results": results,
            "positions": allocation.get("positions", results),
            "summary": summary,
        }

        if self.event_bus is not None:
            self.event_bus.publish(
                "PortfolioAllocated",
                payload={
                    "account_capital": summary.get("account_capital", 0),
                    "capital_allocated": summary.get("capital_allocated", 0),
                    "remaining_cash": summary.get("remaining_cash", 0),
                    "portfolio_risk_pct": summary.get(
                        "portfolio_risk_pct", 0
                    ),
                    "active_positions": summary.get("active_positions", 0),
                    "exposure_pct": summary.get("exposure_pct", 0),
                    "status": summary.get("status", "UNKNOWN"),
                    "symbols": [
                        context.symbol
                        for context in synchronized
                    ],
                },
                source=self.NAME,
            )

        return output
