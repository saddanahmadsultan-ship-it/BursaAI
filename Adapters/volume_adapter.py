"""
=========================================================
BursaAI Volume Adapter
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


class VolumeAdapter(BaseAdapter):
    """
    Wrap Core.volume_engine.score_volume(data).

    Stores:
        context.metadata["volume_data"]
        context.analysis.extra["volume"]
        context.analysis.market.volume
    """

    METADATA = EngineMetadata(
        name="Volume Adapter",
        version="6.0",
        priority=60,
        category="analysis",
        dependencies=["Indicator Adapter"],
    )

    def __init__(
        self,
        volume_function: Optional[Callable[[object], Dict]] = None,
    ):
        super().__init__(metadata=self.METADATA)

        if volume_function is None:
            from Core.volume_engine import score_volume
            volume_function = score_volume

        self.volume_function = volume_function

    def validate_context(self, context: AnalysisContext) -> None:
        super().validate_context(context)

        if context.data is None:
            raise DataError(
                "Volume Adapter requires context.data."
            )

        if getattr(context.data, "empty", False):
            raise DataError(
                "Volume Adapter received empty data."
            )

    def run_legacy(self, context: AnalysisContext):
        output = self.volume_function(
            context.data
        )

        if output is None:
            raise DataError(
                "Volume engine returned None."
            )

        if not isinstance(output, dict):
            raise ValidationError(
                "Volume engine output must be a dictionary."
            )

        return output

    def sync_to_context(self, context, legacy_output) -> None:
        volume_data = deepcopy(
            legacy_output
        )

        context.metadata[
            "volume_data"
        ] = volume_data

        context.analysis.extra[
            "volume"
        ] = volume_data

        strength = (
            volume_data.get("strength")
            or volume_data.get("status")
            or volume_data.get("direction")
            or volume_data.get("quality")
            or "UNKNOWN"
        )

        context.analysis.market.volume = str(
            strength
        )

        score = volume_data.get("score")

        if score is not None:
            context.analysis.extra[
                "volume_score"
            ] = self.bridge._safe_float(score)
