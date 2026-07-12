"""
=========================================================
BursaAI Market Regime Adapter
Version : 6.0 Sprint 5A.1
=========================================================
"""

from __future__ import annotations

from copy import deepcopy
from typing import Callable, Dict, Optional

from Adapters.base_adapter import BaseAdapter
from Framework.context import AnalysisContext
from Framework.event_bus import EventBus
from Framework.exceptions import DataError, ValidationError
from Framework.metadata import EngineMetadata
from Framework.service_container import ServiceContainer


class MarketRegimeAdapter(BaseAdapter):
    """
    Wrap:
        Core.market_regime_engine.apply_market_regime_engine(data, result)

    Synchronizes:
        context.analysis.market.regime
        context.analysis.market.regime_score
        context.analysis.score.regime_bonus
        context.analysis.score.regime_penalty
        context.analysis.score.final

    Publishes:
        MarketRegimeCompleted
    """

    METADATA = EngineMetadata(
        name="Market Regime Adapter",
        version="6.0",
        priority=90,
        category="market",
        dependencies=[
            "Indicator Adapter",
            "Smart Money Adapter",
        ],
    )

    def __init__(
        self,
        regime_function: Optional[
            Callable[[object, Dict], Dict]
        ] = None,
        services: Optional[ServiceContainer] = None,
        event_bus: Optional[EventBus] = None,
    ):
        super().__init__(metadata=self.METADATA)

        if regime_function is None:
            from Core.market_regime_engine import (
                apply_market_regime_engine,
            )
            regime_function = apply_market_regime_engine

        self.regime_function = regime_function
        self.services = services

        if event_bus is not None:
            self.event_bus = event_bus
        elif (
            services is not None
            and services.contains("event_bus")
        ):
            self.event_bus = services.resolve(
                "event_bus"
            )
        else:
            self.event_bus = None

    def validate_context(
        self,
        context: AnalysisContext,
    ) -> None:
        super().validate_context(context)

        if context.data is None:
            raise DataError(
                "Market Regime Adapter requires context.data."
            )

        if getattr(context.data, "empty", False):
            raise DataError(
                "Market Regime Adapter received empty data."
            )

    def run_legacy(
        self,
        context: AnalysisContext,
    ):
        legacy_result = self.bridge.context_to_legacy(
            context
        )

        output = self.regime_function(
            context.data,
            legacy_result,
        )

        if output is None:
            raise ValidationError(
                "Market Regime engine returned None."
            )

        if not isinstance(output, dict):
            raise ValidationError(
                "Market Regime output must be a dictionary."
            )

        return output

    def sync_to_context(
        self,
        context,
        legacy_output,
    ) -> None:
        output = deepcopy(
            legacy_output
        )

        context.metadata[
            "market_regime_data"
        ] = output

        context.analysis.extra[
            "market_regime"
        ] = output

        self.bridge.legacy_to_context(
            legacy=output,
            context=context,
        )

        if self.event_bus is not None:
            self.event_bus.publish(
                "MarketRegimeCompleted",
                payload={
                    "symbol": context.symbol,
                    "regime": (
                        context.analysis.market.regime
                    ),
                    "regime_score": (
                        context.analysis.market.regime_score
                    ),
                    "regime_bonus": (
                        context.analysis.score.regime_bonus
                    ),
                    "regime_penalty": (
                        context.analysis.score.regime_penalty
                    ),
                    "final_score": (
                        context.analysis.score.final
                    ),
                },
                source=self.name,
            )
