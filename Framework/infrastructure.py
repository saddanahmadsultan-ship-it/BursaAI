"""
=========================================================
BursaAI Infrastructure Bootstrap
Version : 6.0 Sprint 5A.0
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from Framework.cache import CacheManager
from Framework.configuration import FrameworkConfiguration
from Framework.event_bus import EventBus
from Framework.plugin_manager import PluginManager
from Framework.service_container import ServiceContainer


@dataclass(slots=True)
class InfrastructureBundle:
    configuration: FrameworkConfiguration
    services: ServiceContainer
    events: EventBus
    cache: CacheManager
    plugins: PluginManager


def build_infrastructure(
    configuration: FrameworkConfiguration | None = None,
) -> InfrastructureBundle:
    config = configuration or FrameworkConfiguration()
    config.validate()

    services = ServiceContainer()
    events = EventBus()
    cache = CacheManager()
    plugins = PluginManager(
        services=services
    )

    services.register_instance(
        "configuration",
        config,
    )

    services.register_instance(
        "event_bus",
        events,
    )

    services.register_instance(
        "cache",
        cache,
    )

    services.register_instance(
        "plugin_manager",
        plugins,
    )

    return InfrastructureBundle(
        configuration=config,
        services=services,
        events=events,
        cache=cache,
        plugins=plugins,
    )
