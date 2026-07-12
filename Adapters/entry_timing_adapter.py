"""
=========================================================
BursaAI Entry Timing Adapter
Version : 6.0 Sprint 5A.2
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


class EntryTimingAdapter(BaseAdapter):
    """
    Wrap:
        Core.entry_timing_engine.apply_entry_timing_engine(data, result)

    Synchronizes:
        context.analysis.timing.score
        context.analysis.timing.status
        context.analysis.timing.action
        context.analysis.timing.entry_zone_low
        context.analysis.timing.entry_zone_high
        context.analysis.timing.reasons
        context.analysis.timing.warnings

    Publishes:
        EntryTimingCompleted
    """

    METADATA = EngineMetadata(
        name="Entry Timing Adapter",
        version="6.0",
        priority=100,
        category="execution",
        dependencies=[
            "Indicator Adapter",
            "Market Regime Adapter",
        ],
    )

    def __init__(
        self,
        timing_function: Optional[
            Callable[[object, Dict], Dict]
        ] = None,
        services: Optional[ServiceContainer] = None,
        event_bus: Optional[EventBus] = None,
    ):
        super().__init__(metadata=self.METADATA)

        if timing_function is None:
            from Core.entry_timing_engine import (
                apply_entry_timing_engine,
            )
            timing_function = apply_entry_timing_engine

        self.timing_function = timing_function
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

    def validate_context(
        self,
        context: AnalysisContext,
    ) -> None:
        super().validate_context(context)

        if context.data is None:
            raise DataError(
                "Entry Timing Adapter requires context.data."
            )

        if getattr(context.data, "empty", False):
            raise DataError(
                "Entry Timing Adapter received empty data."
            )

    def run_legacy(
        self,
        context: AnalysisContext,
    ):
        legacy_result = self.bridge.context_to_legacy(
            context
        )

        output = self.timing_function(
            context.data,
            legacy_result,
        )

        if output is None:
            raise ValidationError(
                "Entry Timing engine returned None."
            )

        if not isinstance(output, dict):
            raise ValidationError(
                "Entry Timing output must be a dictionary."
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
            "entry_timing_data"
        ] = output

        context.analysis.extra[
            "entry_timing"
        ] = output

        self.bridge.legacy_to_context(
            legacy=output,
            context=context,
        )

        if self.event_bus is not None:
            self.event_bus.publish(
                "EntryTimingCompleted",
                payload={
                    "symbol": context.symbol,
                    "score": (
                        context.analysis.timing.score
                    ),
                    "status": (
                        context.analysis.timing.status
                    ),
                    "action": (
                        context.analysis.timing.action
                    ),
                    "entry_zone_low": (
                        context.analysis.timing.entry_zone_low
                    ),
                    "entry_zone_high": (
                        context.analysis.timing.entry_zone_high
                    ),
                    "reasons": list(
                        context.analysis.timing.reasons
                    ),
                    "warnings": list(
                        context.analysis.timing.warnings
                    ),
                },
                source=self.name,
            )
