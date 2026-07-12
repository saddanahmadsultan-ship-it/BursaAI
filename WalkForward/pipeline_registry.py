"""
=========================================================
BursaAI Walk Forward Pipeline Registry
Version : 6.0 Sprint 6F.8
=========================================================
"""

from __future__ import annotations

from typing import Any, Dict, List

from Framework.exceptions import ConfigurationError


class WalkForwardPipelineRegistry:
    def __init__(self):
        self._pipelines: Dict[str, Any] = {}

    def register(
        self,
        name: str,
        pipeline: Any,
        *,
        replace: bool = False,
    ) -> None:
        key = str(name).strip().lower()

        if not key:
            raise ConfigurationError(
                "Pipeline name cannot be empty."
            )

        if pipeline is None:
            raise ConfigurationError(
                "Pipeline cannot be None."
            )

        if key in self._pipelines and not replace:
            raise ConfigurationError(
                f"Pipeline already registered: {key}"
            )

        self._pipelines[key] = pipeline

    def get(self, name: str) -> Any:
        key = str(name).strip().lower()

        if key not in self._pipelines:
            raise ConfigurationError(
                f"Pipeline not found: {key}"
            )

        return self._pipelines[key]

    def names(self) -> List[str]:
        return sorted(self._pipelines)

    def unregister(self, name: str) -> None:
        self._pipelines.pop(
            str(name).strip().lower(),
            None,
        )
