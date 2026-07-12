"""
=========================================================
BursaAI Score Adapter
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


class ScoreAdapter(BaseAdapter):
    """
    Wrap Core.scorer.calculate_score(data).

    Stores complete legacy output in:
        context.metadata["score_data"]

    Synchronizes:
        score
        trend
        momentum
        volume
        volatility
        risk
    """

    METADATA = EngineMetadata(
        name="Score Adapter",
        version="6.0",
        priority=30,
        category="analysis",
        dependencies=["Indicator Adapter"],
    )

    def __init__(
        self,
        scorer: Optional[Callable[[object], Dict]] = None,
    ):
        super().__init__(metadata=self.METADATA)

        if scorer is None:
            from Core.scorer import calculate_score
            scorer = calculate_score

        self.scorer = scorer

    def validate_context(self, context: AnalysisContext) -> None:
        super().validate_context(context)

        if context.data is None:
            raise DataError(
                "Score Adapter requires indicator-enriched context.data."
            )

        if getattr(context.data, "empty", False):
            raise DataError(
                "Score Adapter received empty data."
            )

    def run_legacy(self, context: AnalysisContext):
        output = self.scorer(context.data)

        if output is None:
            raise DataError(
                "Scorer returned None."
            )

        if not isinstance(output, dict):
            raise ValidationError(
                "Scorer output must be a dictionary."
            )

        return output

    def sync_to_context(self, context, legacy_output) -> None:
        score_data = deepcopy(legacy_output)

        context.metadata["score_data"] = score_data

        raw_score = score_data.get(
            "score",
            score_data.get(
                "raw_score",
                score_data.get("raw", 0),
            ),
        )

        legacy_patch = {
            "RawScore": raw_score,
            "Score": raw_score,
        }

        grade = score_data.get("grade")

        if grade is not None:
            legacy_patch["Grade"] = grade

        context.analysis.extra["score_data"] = deepcopy(
            score_data
        )

        sections = {
            "trend": score_data.get("trend", {}),
            "momentum": score_data.get("momentum", {}),
            "volume": score_data.get("volume", {}),
            "volatility": score_data.get("volatility", {}),
            "risk": score_data.get("risk", {}),
        }

        context.analysis.extra.update(
            deepcopy(sections)
        )

        self.bridge.legacy_to_context(
            legacy=legacy_patch,
            context=context,
        )

        # Preserve meaningful text values when available.
        trend = sections["trend"]

        if isinstance(trend, dict):
            direction = (
                trend.get("direction")
                or trend.get("trend")
                or trend.get("strength")
            )

            if direction is not None:
                context.analysis.market.trend = str(
                    direction
                )

        momentum = sections["momentum"]

        if isinstance(momentum, dict):
            description = (
                momentum.get("direction")
                or momentum.get("strength")
                or momentum.get("status")
            )

            if description is not None:
                context.analysis.market.momentum = str(
                    description
                )

        volume = sections["volume"]

        if isinstance(volume, dict):
            strength = (
                volume.get("strength")
                or volume.get("status")
            )

            if strength is not None:
                context.analysis.market.volume = str(
                    strength
                )

        volatility = sections["volatility"]

        if isinstance(volatility, dict):
            status = (
                volatility.get("status")
                or volatility.get("level")
                or volatility.get("strength")
            )

            if status is not None:
                context.analysis.market.volatility = str(
                    status
                )
