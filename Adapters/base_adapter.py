"""
=========================================================
BursaAI Base Adapter
Version : 6.0 Sprint 4A
=========================================================
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from Framework.base_engine import BaseEngine
from Framework.context import AnalysisContext
from Framework.exceptions import EngineError
from Framework.legacy_bridge import LegacyBridge
from Framework.metadata import EngineMetadata


class BaseAdapter(BaseEngine):
    """
    Base class for adapters that wrap existing Core functions.

    Subclasses should implement:
        run_legacy(context) -> Any

    Optional:
        sync_to_context(context, legacy_output)
    """

    METADATA = EngineMetadata(
        name="Base Adapter",
        version="6.0",
        priority=100,
        enabled=True,
        category="adapter",
    )

    def __init__(
        self,
        metadata: Optional[EngineMetadata] = None,
        bridge: Optional[LegacyBridge] = None,
    ):
        super().__init__(metadata=metadata)
        self.bridge = bridge or LegacyBridge()

    def validate_context(self, context: AnalysisContext) -> None:
        super().validate_context(context)

        if not context.symbol:
            raise EngineError(
                f"{self.name} requires a valid symbol."
            )

    def run_legacy(self, context: AnalysisContext) -> Any:
        raise NotImplementedError(
            f"{self.name} must implement run_legacy()."
        )

    def sync_to_context(
        self,
        context: AnalysisContext,
        legacy_output: Any,
    ) -> None:
        """
        Default behavior:
        - if output is dict, merge into legacy result
        - sync bridge back into AnalysisModel
        """

        if legacy_output is None:
            return

        if isinstance(legacy_output, dict):
            current = self.bridge.context_to_legacy(context)
            current.update(legacy_output)

            self.bridge.legacy_to_context(
                legacy=current,
                context=context,
            )

            return

        context.metadata.setdefault(
            "adapter_outputs",
            {}
        )[self.name] = legacy_output

    def process(
        self,
        context: AnalysisContext,
    ) -> Dict[str, Any]:
        legacy_output = self.run_legacy(context)

        self.sync_to_context(
            context=context,
            legacy_output=legacy_output,
        )

        return {
            "adapter": self.name,
            "legacy_output": legacy_output,
        }
