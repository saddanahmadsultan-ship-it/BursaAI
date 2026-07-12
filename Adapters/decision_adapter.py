"""
=========================================================
BursaAI Decision Adapter
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


class DecisionAdapter(BaseAdapter):
    """
    Wrap:
        Core.decision.make_decision(result)

    Builds the exact lower-case input expected by the current
    Decision Engine from the latest indicator row and context.
    """

    METADATA = EngineMetadata(
        name="Decision Adapter",
        version="6.0",
        priority=140,
        category="decision",
        dependencies=[
            "Strategy Adapter",
        ],
    )

    def __init__(
        self,
        decision_function: Optional[Callable[[Dict], Dict]] = None,
        services: Optional[ServiceContainer] = None,
        event_bus: Optional[EventBus] = None,
    ):
        super().__init__(metadata=self.METADATA)

        if decision_function is None:
            from Core.decision import make_decision
            decision_function = make_decision

        self.decision_function = decision_function
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
                "Decision Adapter requires context.data."
            )

    def _last(self, context: AnalysisContext, key: str, default=0):
        last = context.data.iloc[-1]

        try:
            return last.get(key, default)
        except AttributeError:
            try:
                return last[key]
            except Exception:
                return default

    def _bool_last(self, context, key):
        return bool(self._last(context, key, False))

    def run_legacy(self, context: AnalysisContext):
        macd = self.bridge._safe_float(
            self._last(context, "MACD", 0)
        )
        macd_signal_value = self.bridge._safe_float(
            self._last(context, "MACD_SIGNAL", 0)
        )

        decision_input = {
            "price": self.bridge._safe_float(
                self._last(context, "Close", context.analysis.identity.price)
            ),
            "ema20": self.bridge._safe_float(
                self._last(
                    context,
                    "EMA20",
                    self._last(context, "MA20", 0),
                )
            ),
            "ema50": self.bridge._safe_float(
                self._last(
                    context,
                    "EMA50",
                    self._last(context, "MA50", 0),
                )
            ),
            "ema200": self.bridge._safe_float(
                self._last(
                    context,
                    "EMA200",
                    self._last(context, "MA200", 0),
                )
            ),
            "ema20_slope": self.bridge._safe_float(
                self._last(context, "EMA20_SLOPE", 0)
            ),
            "higher_high": self._bool_last(context, "HIGHER_HIGH"),
            "higher_low": self._bool_last(context, "HIGHER_LOW"),
            "lower_high": self._bool_last(context, "LOWER_HIGH"),
            "breakout": self._bool_last(context, "BREAKOUT"),
            "breakdown": self._bool_last(context, "BREAKDOWN"),
            "vwap": self.bridge._safe_float(
                self._last(context, "VWAP", 0)
            ),
            "rsi": self.bridge._safe_float(
                self._last(context, "RSI", 50)
            ),
            "stoch": self.bridge._safe_float(
                self._last(context, "STOCH", 50)
            ),
            "cci": self.bridge._safe_float(
                self._last(context, "CCI", 0)
            ),
            "roc": self.bridge._safe_float(
                self._last(context, "ROC", 0)
            ),
            "macd_signal": (
                "Bullish"
                if macd >= macd_signal_value
                else "Bearish"
            ),
            "macd": macd,
            "macd_histogram": self.bridge._safe_float(
                self._last(context, "MACD_HISTOGRAM", 0)
            ),
            "volume_score": self.bridge._safe_float(
                context.analysis.extra.get("volume_score", 0)
            ),
            "obv_bullish": (
                self.bridge._safe_float(
                    self._last(context, "OBV", 0)
                )
                >=
                self.bridge._safe_float(
                    self._last(context, "OBV_MA20", 0)
                )
            ),
            "atr_percent": self.bridge._safe_float(
                self._last(context, "ATR_PERCENT", 0)
            ),
            "confidence": context.analysis.confidence,
            "rr": context.analysis.trade.risk_reward,
            "trend": context.analysis.market.trend,
            "score": context.analysis.score.final,
        }

        context.metadata["decision_input"] = deepcopy(decision_input)

        output = self.decision_function(decision_input)

        if not isinstance(output, dict):
            raise ValidationError(
                "Decision output must be a dictionary."
            )

        return output

    def sync_to_context(self, context, legacy_output) -> None:
        output = deepcopy(legacy_output)

        context.metadata["decision_data"] = output
        context.analysis.extra["decision"] = output

        context.analysis.trade.decision_signal = str(
            output.get("recommendation", "UNKNOWN")
        )
        context.analysis.trade.rating = str(
            output.get("rating", "UNKNOWN")
        )

        context.analysis.summary = str(
            output.get("summary", "")
        )
        context.analysis.reasons = self.bridge._safe_list(
            output.get("analysis", [])
        )
        context.analysis.warnings = self.bridge._safe_list(
            output.get("warnings", [])
        )
        context.analysis.extra["decision_quality"] = (
            self.bridge._safe_float(
                output.get("quality", 0)
            )
        )

        if self.event_bus is not None:
            self.event_bus.publish(
                "DecisionCompleted",
                payload={
                    "symbol": context.symbol,
                    "recommendation": (
                        context.analysis.trade.decision_signal
                    ),
                    "rating": context.analysis.trade.rating,
                    "quality": context.analysis.extra["decision_quality"],
                    "summary": context.analysis.summary,
                    "analysis": list(context.analysis.reasons),
                    "warnings": list(context.analysis.warnings),
                },
                source=self.name,
            )
