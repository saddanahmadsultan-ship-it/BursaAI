"""
=========================================================
BursaAI Momentum Adapter
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


class MomentumAdapter(BaseAdapter):
    """
    Wrap Core.momentum_engine.score_momentum(data).

    Stores complete output in:
        context.metadata["momentum_data"]
        context.analysis.extra["momentum"]
    """

    METADATA = EngineMetadata(
        name="Momentum Adapter",
        version="6.0",
        priority=50,
        category="analysis",
        dependencies=["Indicator Adapter"],
    )

    def __init__(
        self,
        momentum_function: Optional[Callable[[object], Dict]] = None,
    ):
        super().__init__(metadata=self.METADATA)

        if momentum_function is None:
            from Core.momentum_engine import score_momentum
            momentum_function = score_momentum

        self.momentum_function = momentum_function

    def validate_context(self, context: AnalysisContext) -> None:
        super().validate_context(context)

        if context.data is None:
            raise DataError(
                "Momentum Adapter requires context.data."
            )

    def run_legacy(self, context: AnalysisContext):
        output = self.momentum_function(
            context.data
        )

        if output is None:
            raise DataError(
                "Momentum engine returned None."
            )

        if not isinstance(output, dict):
            raise ValidationError(
                "Momentum engine output must be a dictionary."
            )

        return output

    def sync_to_context(self, context, legacy_output) -> None:
        momentum_data = deepcopy(
            legacy_output
        )

        context.metadata[
            "momentum_data"
        ] = momentum_data

        context.analysis.extra[
            "momentum"
        ] = momentum_data

        description = (
            momentum_data.get("direction")
            or momentum_data.get("status")
            or momentum_data.get("strength")
            or momentum_data.get("momentum")
            or "UNKNOWN"
        )

        context.analysis.market.momentum = str(
            description
        )

        score = momentum_data.get("score")

        if score is not None:
            context.analysis.extra[
                "momentum_score"
            ] = self.bridge._safe_float(score)
