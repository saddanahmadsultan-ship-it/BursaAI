"""
=========================================================
BursaAI Strategy Adapter
Version : 6.0 Sprint 5B
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


class StrategyAdapter(BaseAdapter):
    """
    Wrap:
        Core.strategy.trading_signal(
            data,
            score_data,
            trend_data,
            momentum_data,
            volume_data,
            confidence_data,
        )
    """

    METADATA = EngineMetadata(
        name="Strategy Adapter",
        version="6.0",
        priority=130,
        category="decision",
        dependencies=[
            "Confidence Adapter",
        ],
    )

    def __init__(
        self,
        strategy_function: Optional[Callable[..., Dict]] = None,
        services: Optional[ServiceContainer] = None,
        event_bus: Optional[EventBus] = None,
    ):
        super().__init__(metadata=self.METADATA)

        if strategy_function is None:
            from Core.strategy import trading_signal
            strategy_function = trading_signal

        self.strategy_function = strategy_function
        self.services = services

        if event_bus is not None:
            self.event_bus = event_bus
        elif services is not None and services.contains("event_bus"):
            self.event_bus = services.resolve("event_bus")
        else:
            self.event_bus = None

    def validate_context(self, context: AnalysisContext) -> None:
        super().validate_context(context)

        if context.data is None:
            raise DataError(
                "Strategy Adapter requires context.data."
            )

    def _section(self, context: AnalysisContext, key: str) -> Dict:
        value = context.analysis.extra.get(key, {})
        return deepcopy(value) if isinstance(value, dict) else {}

    def run_legacy(self, context: AnalysisContext):
        score_data = deepcopy(
            context.metadata.get(
                "score_data",
                self._section(context, "score_data"),
            )
        )
        score_data.setdefault("score", context.analysis.score.raw)

        trend_data = self._section(context, "trend")
        trend_data.setdefault("direction", context.analysis.market.trend)

        momentum_data = self._section(context, "momentum")
        momentum_data.setdefault("quality", context.analysis.market.momentum)

        volume_data = self._section(context, "volume")
        volume_data.setdefault(
            "score",
            context.analysis.extra.get("volume_score", 0),
        )

        confidence_data = deepcopy(
            context.metadata.get("confidence_data", {})
        )
        confidence_data.setdefault(
            "confidence",
            context.analysis.confidence,
        )
        confidence_data.setdefault(
            "level",
            context.analysis.confidence_level,
        )

        output = self.strategy_function(
            context.data,
            score_data,
            trend_data,
            momentum_data,
            volume_data,
            confidence_data,
        )

        if not isinstance(output, dict):
            raise ValidationError(
                "Strategy output must be a dictionary."
            )

        return output

    def sync_to_context(self, context, legacy_output) -> None:
        output = deepcopy(legacy_output)

        context.metadata["strategy_data"] = output
        context.analysis.extra["strategy"] = output

        context.analysis.trade.signal = str(
            output.get("strategy", "UNKNOWN")
        )
        context.analysis.trade.entry = self.bridge._safe_float(
            output.get("entry", 0)
        )
        context.analysis.trade.stop_loss = self.bridge._safe_float(
            output.get("stoploss", 0)
        )
        context.analysis.trade.target = self.bridge._safe_float(
            output.get("target", 0)
        )
        context.analysis.trade.risk_reward = self.bridge._safe_float(
            output.get("rr", 0)
        )

        context.analysis.extra["strategy_bullish"] = bool(
            output.get("bullish", False)
        )
        context.analysis.extra["strategy_warnings"] = self.bridge._safe_list(
            output.get("warning", [])
        )

        if self.event_bus is not None:
            self.event_bus.publish(
                "StrategyGenerated",
                payload={
                    "symbol": context.symbol,
                    "strategy": context.analysis.trade.signal,
                    "entry": context.analysis.trade.entry,
                    "stop_loss": context.analysis.trade.stop_loss,
                    "target": context.analysis.trade.target,
                    "risk_reward": context.analysis.trade.risk_reward,
                    "warnings": list(
                        context.analysis.extra["strategy_warnings"]
                    ),
                },
                source=self.name,
            )
