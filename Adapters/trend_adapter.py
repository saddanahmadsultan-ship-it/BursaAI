"""
=========================================================
BursaAI Trend Adapter
Version : 6.0 Sprint 4C
=========================================================
"""

from __future__ import annotations

from copy import deepcopy
from typing import Callable, Dict, Optional

from Adapters.base_adapter import BaseAdapter
from Framework.context import AnalysisContext
from Framework.exceptions import DataError, ValidationError
from Framework.metadata import EngineMetadata


class TrendAdapter(BaseAdapter):
    """
    Wrap Core.trend_engine.score_trend(data).

    Stores complete output in:
        context.metadata["trend_data"]
        context.analysis.extra["trend"]
    """

    METADATA = EngineMetadata(
        name="Trend Adapter",
        version="6.0",
        priority=40,
        category="analysis",
        dependencies=["Indicator Adapter"],
    )

    def __init__(
        self,
        trend_function: Optional[Callable[[object], Dict]] = None,
    ):
        super().__init__(metadata=self.METADATA)

        if trend_function is None:
            from Core.trend_engine import score_trend
            trend_function = score_trend

        self.trend_function = trend_function

    def validate_context(self, context: AnalysisContext) -> None:
        super().validate_context(context)

        if context.data is None:
            raise DataError(
                "Trend Adapter requires context.data."
            )

    def run_legacy(self, context: AnalysisContext):
        output = self.trend_function(
            context.data
        )

        if output is None:
            raise DataError(
                "Trend engine returned None."
            )

        if not isinstance(output, dict):
            raise ValidationError(
                "Trend engine output must be a dictionary."
            )

        return output

    def sync_to_context(self, context, legacy_output) -> None:
        trend_data = deepcopy(legacy_output)

        context.metadata["trend_data"] = trend_data
        context.analysis.extra["trend"] = trend_data

        direction = (
            trend_data.get("direction")
            or trend_data.get("trend")
            or trend_data.get("status")
            or trend_data.get("strength")
            or "UNKNOWN"
        )

        context.analysis.market.trend = str(
            direction
        )

        score = trend_data.get("score")

        if score is not None:
            context.analysis.extra[
                "trend_score"
            ] = self.bridge._safe_float(score)
