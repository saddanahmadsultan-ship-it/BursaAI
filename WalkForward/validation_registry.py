"""
=========================================================
BursaAI Validation Function Registry
Version : 6.0 Sprint 6F.4
=========================================================
"""

from __future__ import annotations

from typing import Callable, Dict, List

from Framework.exceptions import ConfigurationError


class ValidationRegistry:
    def __init__(self):
        self._validators: Dict[str, Callable] = {}

    def register(
        self,
        name: str,
        validator: Callable,
        *,
        replace: bool = False,
    ) -> None:
        key = str(name).strip().lower()

        if not key:
            raise ConfigurationError(
                "Validator name cannot be empty."
            )

        if not callable(validator):
            raise ConfigurationError(
                "Validator must be callable."
            )

        if key in self._validators and not replace:
            raise ConfigurationError(
                f"Validator already registered: {key}"
            )

        self._validators[key] = validator

    def get(self, name: str) -> Callable:
        key = str(name).strip().lower()

        if key not in self._validators:
            raise ConfigurationError(
                f"Validator not found: {key}"
            )

        return self._validators[key]

    def names(self) -> List[str]:
        return sorted(self._validators)
