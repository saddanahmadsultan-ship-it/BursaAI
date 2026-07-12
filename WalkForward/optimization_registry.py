"""
=========================================================
BursaAI Optimization Registry
Version : 6.0 Sprint 6F.6B
=========================================================
"""

from __future__ import annotations

from typing import Any, Dict, List

from Framework.exceptions import ConfigurationError


class OptimizationRegistry:
    def __init__(self):
        self._optimizers: Dict[str, Any] = {}

    def register(
        self,
        name: str,
        optimizer: Any,
        *,
        replace: bool = False,
    ) -> None:
        key = str(name).strip().lower()

        if not key:
            raise ConfigurationError(
                "Optimizer name cannot be empty."
            )

        if optimizer is None:
            raise ConfigurationError(
                "Optimizer cannot be None."
            )

        if key in self._optimizers and not replace:
            raise ConfigurationError(
                f"Optimizer already registered: {key}"
            )

        self._optimizers[key] = optimizer

    def get(self, name: str) -> Any:
        key = str(name).strip().lower()

        if key not in self._optimizers:
            raise ConfigurationError(
                f"Optimizer not found: {key}"
            )

        return self._optimizers[key]

    def names(self) -> List[str]:
        return sorted(self._optimizers)

    def unregister(self, name: str) -> None:
        self._optimizers.pop(
            str(name).strip().lower(),
            None,
        )
