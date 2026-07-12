"""
=========================================================
BursaAI Service Container
Version : 6.0 Sprint 5A.0
=========================================================
"""

from __future__ import annotations

from typing import Any, Callable, Dict

from Framework.exceptions import ConfigurationError


class ServiceContainer:
    """
    Lightweight dependency injection container.

    Supports:
    - singleton instances
    - lazy factories
    - existence checks
    - replacement
    """

    def __init__(self):
        self._instances: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[["ServiceContainer"], Any]] = {}

    def register_instance(
        self,
        name: str,
        instance: Any,
        replace: bool = False,
    ) -> None:
        key = self._normalize_name(name)

        if self.contains(key) and not replace:
            raise ConfigurationError(
                f"Service already registered: {key}"
            )

        self._instances[key] = instance
        self._factories.pop(key, None)

    def register_factory(
        self,
        name: str,
        factory: Callable[["ServiceContainer"], Any],
        replace: bool = False,
    ) -> None:
        key = self._normalize_name(name)

        if not callable(factory):
            raise ConfigurationError(
                "Service factory must be callable."
            )

        if self.contains(key) and not replace:
            raise ConfigurationError(
                f"Service already registered: {key}"
            )

        self._factories[key] = factory
        self._instances.pop(key, None)

    def resolve(self, name: str) -> Any:
        key = self._normalize_name(name)

        if key in self._instances:
            return self._instances[key]

        if key in self._factories:
            instance = self._factories[key](self)
            self._instances[key] = instance
            return instance

        raise ConfigurationError(
            f"Service not found: {key}"
        )

    def contains(self, name: str) -> bool:
        key = self._normalize_name(name)
        return (
            key in self._instances
            or key in self._factories
        )

    def unregister(self, name: str) -> None:
        key = self._normalize_name(name)
        self._instances.pop(key, None)
        self._factories.pop(key, None)

    def clear(self) -> None:
        self._instances.clear()
        self._factories.clear()

    def names(self) -> list[str]:
        return sorted(
            set(self._instances)
            | set(self._factories)
        )

    def _normalize_name(self, name: str) -> str:
        key = str(name).strip()

        if not key:
            raise ConfigurationError(
                "Service name cannot be empty."
            )

        return key
