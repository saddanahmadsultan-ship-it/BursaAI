"""
=========================================================
BursaAI AI Brain Adapter
Version : 6.0 Sprint 5A.3
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


class AIBrainAdapter(BaseAdapter):
    """
    Wrap:
        Core.ai_brain.apply_ai_brain(result)

    Synchronizes:
        context.analysis.ai.conviction_score
        context.analysis.ai.conviction_level
        context.analysis.ai.signal
        context.analysis.ai.prediction_stability
        context.analysis.ai.execution_quality
        context.analysis.ai.strengths
        context.analysis.ai.weaknesses
        context.analysis.ai.summary
        context.analysis.ai.components
        context.analysis.ai.contributions

    Publishes:
        AIBrainCompleted
    """

    METADATA = EngineMetadata(
        name="AI Brain Adapter",
        version="6.0",
        priority=110,
        category="ai",
        dependencies=[
            "Market Regime Adapter",
            "Entry Timing Adapter",
        ],
    )

    def __init__(
        self,
        brain_function: Optional[
            Callable[[Dict], Dict]
        ] = None,
        services: Optional[ServiceContainer] = None,
        event_bus: Optional[EventBus] = None,
    ):
        super().__init__(metadata=self.METADATA)

        if brain_function is None:
            from Core.ai_brain import apply_ai_brain
            brain_function = apply_ai_brain

        self.brain_function = brain_function
        self.services = services

        if event_bus is not None:
            self.event_bus = event_bus
        elif (
            services is not None
            and services.contains("event_bus")
        ):
            self.event_bus = services.resolve(
                "event_bus"
            )
        else:
            self.event_bus = None

    def run_legacy(
        self,
        context: AnalysisContext,
    ):
        legacy_result = self.bridge.context_to_legacy(
            context
        )

        output = self.brain_function(
            legacy_result
        )

        if output is None:
            raise ValidationError(
                "AI Brain returned None."
            )

        if not isinstance(output, dict):
            raise ValidationError(
                "AI Brain output must be a dictionary."
            )

        return output

    def sync_to_context(
        self,
        context,
        legacy_output,
    ) -> None:
        output = deepcopy(
            legacy_output
        )

        context.metadata[
            "ai_brain_data"
        ] = output

        context.analysis.extra[
            "ai_brain"
        ] = output

        self.bridge.legacy_to_context(
            legacy=output,
            context=context,
        )

        if self.event_bus is not None:
            self.event_bus.publish(
                "AIBrainCompleted",
                payload={
                    "symbol": context.symbol,
                    "conviction_score": (
                        context.analysis.ai.conviction_score
                    ),
                    "conviction_level": (
                        context.analysis.ai.conviction_level
                    ),
                    "ai_signal": (
                        context.analysis.ai.signal
                    ),
                    "prediction_stability": (
                        context.analysis.ai.prediction_stability
                    ),
                    "execution_quality": (
                        context.analysis.ai.execution_quality
                    ),
                    "summary": (
                        context.analysis.ai.summary
                    ),
                    "strengths": list(
                        context.analysis.ai.strengths
                    ),
                    "weaknesses": list(
                        context.analysis.ai.weaknesses
                    ),
                },
                source=self.name,
            )
