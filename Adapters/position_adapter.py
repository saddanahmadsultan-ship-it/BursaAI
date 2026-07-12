"""
=========================================================
BursaAI Position Adapter
Version : 6.0 Sprint 5C.2
=========================================================
"""

from __future__ import annotations

from copy import deepcopy
from typing import Callable, Dict, Optional

from Adapters.base_adapter import BaseAdapter
from Framework.context import AnalysisContext
from Framework.event_bus import EventBus
from Framework.exceptions import ValidationError
from Framework.metadata import EngineMetadata
from Framework.service_container import ServiceContainer


class PositionAdapter(BaseAdapter):
    """
    Wrap:
        Core.position_engine.apply_position_engine(result)
    """

    METADATA = EngineMetadata(
        name="Position Adapter",
        version="6.0",
        priority=160,
        category="position",
        dependencies=["Dynamic Risk Adapter"],
    )

    def __init__(
        self,
        position_function: Optional[Callable[[Dict], Dict]] = None,
        services: Optional[ServiceContainer] = None,
        event_bus: Optional[EventBus] = None,
    ):
        super().__init__(metadata=self.METADATA)

        if position_function is None:
            from Core.position_engine import apply_position_engine
            position_function = apply_position_engine

        self.position_function = position_function
        self.services = services

        if event_bus is not None:
            self.event_bus = event_bus
        elif services is not None and services.contains("event_bus"):
            self.event_bus = services.resolve("event_bus")
        else:
            self.event_bus = None

    def run_legacy(self, context: AnalysisContext):
        output = self.position_function(
            self.bridge.context_to_legacy(context)
        )

        if output is None:
            raise ValidationError(
                "Position Engine returned None."
            )

        if not isinstance(output, dict):
            raise ValidationError(
                "Position Engine output must be a dictionary."
            )

        return output

    def sync_to_context(self, context, legacy_output) -> None:
        output = deepcopy(legacy_output)
        context.metadata["position_data"] = output
        context.analysis.extra["position"] = deepcopy(output)

        position = context.analysis.position

        position.account_capital = self.bridge._safe_float(
            output.get("AccountCapital", 0)
        )
        position.risk_percent = self.bridge._safe_float(
            output.get("RiskPercent", 0)
        )
        position.risk_capital = self.bridge._safe_float(
            output.get("RiskCapital", 0)
        )
        position.risk_per_share = self.bridge._safe_float(
            output.get("RiskPerShare", 0)
        )
        position.shares = self.bridge._safe_int(
            output.get("Shares", 0)
        )
        position.lots = self.bridge._safe_int(
            output.get("Lots", 0)
        )
        position.capital_used = self.bridge._safe_float(
            output.get(
                "CapitalUsed",
                output.get("Capital", 0),
            )
        )
        position.remaining_capital = self.bridge._safe_float(
            output.get("RemainingCapital", 0)
        )
        position.allocation_percent = self.bridge._safe_float(
            output.get("Allocation", 0)
        )
        position.actual_risk_percent = self.bridge._safe_float(
            output.get("ActualRiskPercent", 0)
        )
        position.max_loss = self.bridge._safe_float(
            output.get("MaxLoss", 0)
        )
        position.potential_profit = self.bridge._safe_float(
            output.get("PotentialProfit", 0)
        )
        position.status = str(
            output.get("PositionStatus", "PENDING")
        )
        position.rating = str(
            output.get("PositionRating", "NONE")
        )

        if self.event_bus is not None:
            self.event_bus.publish(
                "PositionCalculated",
                payload={
                    "symbol": context.symbol,
                    "shares": position.shares,
                    "lots": position.lots,
                    "capital_used": position.capital_used,
                    "remaining_capital": position.remaining_capital,
                    "allocation_percent": position.allocation_percent,
                    "risk_percent": position.risk_percent,
                    "actual_risk_percent": position.actual_risk_percent,
                    "max_loss": position.max_loss,
                    "potential_profit": position.potential_profit,
                    "status": position.status,
                    "rating": position.rating,
                },
                source=self.name,
            )
