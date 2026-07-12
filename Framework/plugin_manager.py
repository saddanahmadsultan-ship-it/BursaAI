"""
=========================================================
BursaAI Plugin Manager
Version : 6.0 Sprint 5A.0
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Protocol

from Framework.exceptions import ConfigurationError
from Framework.service_container import ServiceContainer


class PluginProtocol(Protocol):
    name: str
    version: str

    def register(
        self,
        services: ServiceContainer,
    ) -> None:
        ...

    def start(self) -> None:
        ...

    def stop(self) -> None:
        ...


@dataclass(slots=True)
class PluginState:
    name: str
    version: str
    started: bool = False


class PluginManager:
    """
    Register and control framework plugins.
    """

    def __init__(
        self,
        services: ServiceContainer,
    ):
        self.services = services
        self._plugins: Dict[str, PluginProtocol] = {}
        self._states: Dict[str, PluginState] = {}

    def register(
        self,
        plugin: PluginProtocol,
        replace: bool = False,
    ) -> None:
        name = str(
            getattr(plugin, "name", "")
        ).strip()

        version = str(
            getattr(plugin, "version", "1.0")
        )

        if not name:
            raise ConfigurationError(
                "Plugin requires a name."
            )

        if name in self._plugins and not replace:
            raise ConfigurationError(
                f"Plugin already registered: {name}"
            )

        plugin.register(
            self.services
        )

        self._plugins[name] = plugin
        self._states[name] = PluginState(
            name=name,
            version=version,
            started=False,
        )

    def start(self, name: str) -> None:
        plugin = self.get(name)
        plugin.start()
        self._states[name].started = True

    def stop(self, name: str) -> None:
        plugin = self.get(name)
        plugin.stop()
        self._states[name].started = False

    def start_all(self) -> None:
        for name in self.names():
            self.start(name)

    def stop_all(self) -> None:
        for name in reversed(self.names()):
            self.stop(name)

    def get(self, name: str) -> PluginProtocol:
        if name not in self._plugins:
            raise ConfigurationError(
                f"Plugin not found: {name}"
            )

        return self._plugins[name]

    def state(self, name: str) -> PluginState:
        if name not in self._states:
            raise ConfigurationError(
                f"Plugin state not found: {name}"
            )

        return self._states[name]

    def names(self) -> List[str]:
        return sorted(self._plugins)

    def unregister(self, name: str) -> None:
        if name in self._states and self._states[name].started:
            self.stop(name)

        self._plugins.pop(name, None)
        self._states.pop(name, None)
