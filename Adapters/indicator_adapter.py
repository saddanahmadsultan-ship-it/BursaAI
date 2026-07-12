"""
=========================================================
BursaAI Indicator Adapter
Version : 6.0 Sprint 4B
=========================================================
"""

from __future__ import annotations

from typing import Callable, Iterable, Optional

from Adapters.base_adapter import BaseAdapter
from Framework.context import AnalysisContext
from Framework.exceptions import DataError, ValidationError
from Framework.metadata import EngineMetadata


class IndicatorAdapter(BaseAdapter):
    """
    Wrap Core.indicators.add_indicators(data).

    Input:
        context.data

    Output:
        context.indicators
        context.data

    context.data is also updated because legacy BursaAI engines
    expect the indicator-enriched DataFrame as their main data.
    """

    METADATA = EngineMetadata(
        name="Indicator Adapter",
        version="6.0",
        priority=20,
        category="indicators",
        dependencies=["Loader Adapter"],
    )

    def __init__(
        self,
        indicator_function: Optional[Callable[[object], object]] = None,
        required_columns: Optional[Iterable[str]] = None,
    ):
        super().__init__(metadata=self.METADATA)

        if indicator_function is None:
            from Core.indicators import add_indicators
            indicator_function = add_indicators

        self.indicator_function = indicator_function
        self.required_columns = [
            str(column)
            for column in (required_columns or [])
        ]

    def validate_context(self, context: AnalysisContext) -> None:
        super().validate_context(context)

        if context.data is None:
            raise DataError(
                "Indicator Adapter requires context.data."
            )

        if getattr(context.data, "empty", False):
            raise DataError(
                "Indicator Adapter received empty market data."
            )

    def run_legacy(self, context: AnalysisContext):
        enriched = self.indicator_function(
            context.data
        )

        if enriched is None:
            raise DataError(
                "Indicator function returned None."
            )

        if getattr(enriched, "empty", False):
            raise DataError(
                "Indicator function returned empty data."
            )

        columns = {
            str(column)
            for column in getattr(
                enriched,
                "columns",
                [],
            )
        }

        missing = [
            column
            for column in self.required_columns
            if column not in columns
        ]

        if missing:
            raise ValidationError(
                "Missing required indicator columns: "
                + ", ".join(missing)
            )

        return enriched

    def sync_to_context(self, context, legacy_output) -> None:
        context.indicators = legacy_output
        context.data = legacy_output

        columns = [
            str(column)
            for column in getattr(
                legacy_output,
                "columns",
                [],
            )
        ]

        context.metadata["indicators_added"] = True
        context.metadata["indicator_rows"] = len(
            legacy_output
        )
        context.metadata["indicator_columns"] = columns
