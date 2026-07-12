"""
=========================================================
BursaAI Smart Money Adapter
Version : 6.0 Sprint 4D
=========================================================
"""

from __future__ import annotations

from copy import deepcopy
from typing import Callable, Dict, Optional

from Adapters.base_adapter import BaseAdapter
from Framework.context import AnalysisContext
from Framework.exceptions import DataError, ValidationError
from Framework.metadata import EngineMetadata


class SmartMoneyAdapter(BaseAdapter):
    """
    Wrap Core.smart_money_engine.apply_smart_money_engine(data, result).

    Stores:
        context.metadata["smart_money_data"]
        context.analysis.extra["smart_money"]
        context.analysis.market.smart_money
    """

    METADATA = EngineMetadata(
        name="Smart Money Adapter",
        version="6.0",
        priority=80,
        category="institutional",
        dependencies=[
            "Indicator Adapter",
            "Quality Gate Adapter",
        ],
    )

    def __init__(
        self,
        smart_money_function: Optional[
            Callable[[object, Dict], Dict]
        ] = None,
    ):
        super().__init__(metadata=self.METADATA)

        if smart_money_function is None:
            from Core.smart_money_engine import (
                apply_smart_money_engine
            )
            smart_money_function = apply_smart_money_engine

        self.smart_money_function = smart_money_function

    def validate_context(self, context: AnalysisContext) -> None:
        super().validate_context(context)

        if context.data is None:
            raise DataError(
                "Smart Money Adapter requires context.data."
            )

        if getattr(context.data, "empty", False):
            raise DataError(
                "Smart Money Adapter received empty data."
            )

    def run_legacy(self, context: AnalysisContext):
        legacy_result = self.bridge.context_to_legacy(
            context
        )

        output = self.smart_money_function(
            context.data,
            legacy_result,
        )

        if output is None:
            raise ValidationError(
                "Smart Money engine returned None."
            )

        if not isinstance(output, dict):
            raise ValidationError(
                "Smart Money output must be a dictionary."
            )

        return output

    def sync_to_context(self, context, legacy_output) -> None:
        output = deepcopy(
            legacy_output
        )

        context.metadata[
            "smart_money_data"
        ] = output

        context.analysis.extra[
            "smart_money"
        ] = output

        self.bridge.legacy_to_context(
            legacy=output,
            context=context,
        )
