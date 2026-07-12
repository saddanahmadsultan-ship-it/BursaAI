"""
=========================================================
BursaAI Confidence Adapter
Version : 6.0 Sprint 5B
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


class ConfidenceAdapter(BaseAdapter):
    """
    Wrap:
        Core.confidence.calculate_confidence(
            trend_data,
            momentum_data,
            volume_data,
            volatility_data,
            risk_data,
            modifier_data,
        )
    """

    METADATA = EngineMetadata(
        name="Confidence Adapter",
        version="6.0",
        priority=120,
        category="decision",
        dependencies=[
            "Score Adapter",
            "AI Brain Adapter",
        ],
    )

    def __init__(
        self,
        confidence_function: Optional[Callable[..., Dict]] = None,
        services: Optional[ServiceContainer] = None,
        event_bus: Optional[EventBus] = None,
    ):
        super().__init__(metadata=self.METADATA)

        if confidence_function is None:
            from Core.confidence import calculate_confidence
            confidence_function = calculate_confidence

        self.confidence_function = confidence_function
        self.services = services

        if event_bus is not None:
            self.event_bus = event_bus
        elif services is not None and services.contains("event_bus"):
            self.event_bus = services.resolve("event_bus")
        else:
            self.event_bus = None

    def _section(self, context: AnalysisContext, key: str) -> Dict:
        value = context.analysis.extra.get(key, {})
        return deepcopy(value) if isinstance(value, dict) else {}

    def run_legacy(self, context: AnalysisContext):
        trend_data = self._section(context, "trend")
        momentum_data = self._section(context, "momentum")
        volume_data = self._section(context, "volume")
        volatility_data = self._section(context, "volatility")
        risk_data = self._section(context, "risk")

        if not trend_data:
            trend_data = {"direction": context.analysis.market.trend}

        if not momentum_data:
            momentum_data = {"quality": context.analysis.market.momentum}

        if not volume_data:
            volume_data = {"strength": context.analysis.market.volume}

        volatility_data.setdefault(
            "level",
            context.analysis.market.volatility,
        )

        risk_data.setdefault(
            "rr",
            context.analysis.trade.risk_reward,
        )

        modifier_data = self._section(context, "modifier")

        if not modifier_data:
            modifier_data = deepcopy(
                context.metadata.get("modifier_data", {})
            )

        modifier_data.setdefault("modifier", 0)

        output = self.confidence_function(
            trend_data,
            momentum_data,
            volume_data,
            volatility_data,
            risk_data,
            modifier_data,
        )

        if not isinstance(output, dict):
            raise ValidationError(
                "Confidence output must be a dictionary."
            )

        return output

    def sync_to_context(self, context, legacy_output) -> None:
        output = deepcopy(legacy_output)

        context.metadata["confidence_data"] = output
        context.analysis.extra["confidence"] = output

        context.analysis.confidence = self.bridge._safe_float(
            output.get("confidence", 0)
        )

        context.analysis.confidence_level = str(
            output.get("level", "UNKNOWN")
        )

        context.analysis.extra["confidence_reasons"] = self.bridge._safe_list(
            output.get("reason", [])
        )

        if self.event_bus is not None:
            self.event_bus.publish(
                "ConfidenceCalculated",
                payload={
                    "symbol": context.symbol,
                    "confidence": context.analysis.confidence,
                    "level": context.analysis.confidence_level,
                    "reasons": list(
                        context.analysis.extra["confidence_reasons"]
                    ),
                },
                source=self.name,
            )
