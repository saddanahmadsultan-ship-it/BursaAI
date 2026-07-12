"""
=========================================================
BursaAI Quality Gate Adapter
Version : 6.0 Sprint 4D
=========================================================
"""

from __future__ import annotations

from copy import deepcopy
from typing import Callable, Dict, Optional

from Adapters.base_adapter import BaseAdapter
from Framework.context import AnalysisContext
from Framework.exceptions import ValidationError
from Framework.metadata import EngineMetadata


class QualityGateAdapter(BaseAdapter):
    """
    Wrap Core.quality_gate.apply_quality_gate(result).

    The adapter converts AnalysisContext to the legacy result dict,
    calls the legacy function, then synchronizes the returned result
    back into AnalysisContext.
    """

    METADATA = EngineMetadata(
        name="Quality Gate Adapter",
        version="6.0",
        priority=70,
        category="quality",
        dependencies=["Score Adapter"],
    )

    def __init__(
        self,
        quality_function: Optional[Callable[[Dict], Dict]] = None,
    ):
        super().__init__(metadata=self.METADATA)

        if quality_function is None:
            from Core.quality_gate import apply_quality_gate
            quality_function = apply_quality_gate

        self.quality_function = quality_function

    def run_legacy(self, context: AnalysisContext):
        legacy_result = self.bridge.context_to_legacy(
            context
        )

        output = self.quality_function(
            legacy_result
        )

        if output is None:
            raise ValidationError(
                "Quality Gate returned None."
            )

        if not isinstance(output, dict):
            raise ValidationError(
                "Quality Gate output must be a dictionary."
            )

        return output

    def sync_to_context(self, context, legacy_output) -> None:
        output = deepcopy(
            legacy_output
        )

        context.metadata[
            "quality_data"
        ] = output

        context.analysis.extra[
            "quality"
        ] = output

        self.bridge.legacy_to_context(
            legacy=output,
            context=context,
        )
