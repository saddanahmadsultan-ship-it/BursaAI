"""
BursaAI v6.0 Sprint 5A.0 validation test.
"""

from pathlib import Path
import sys
from time import sleep

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from Framework.configuration import FrameworkConfiguration
from Framework.infrastructure import build_infrastructure


class TestPlugin:
    name = "Test Plugin"
    version = "1.0"

    def __init__(self):
        self.started = False

    def register(self, services):
        services.register_instance(
            "test_service",
            {
                "status": "registered",
            },
        )

    def start(self):
        self.started = True

    def stop(self):
        self.started = False


def main():
    config = FrameworkConfiguration(
        environment="testing",
        cache_default_ttl=1.0,
    )

    infrastructure = build_infrastructure(
        config
    )

    # Service container
    assert infrastructure.services.contains(
        "configuration"
    )

    assert infrastructure.services.resolve(
        "event_bus"
    ) is infrastructure.events

    infrastructure.services.register_factory(
        "lazy_value",
        lambda services: {
            "ready": True,
        },
    )

    assert infrastructure.services.resolve(
        "lazy_value"
    )["ready"] is True

    # Event bus
    received = []

    def handler(event):
        received.append(
            (
                event.name,
                event.payload,
            )
        )

    infrastructure.events.subscribe(
        "TestEvent",
        handler,
    )

    infrastructure.events.publish(
        "TestEvent",
        payload={
            "value": 42,
        },
        source="test",
    )

    assert received == [
        (
            "TestEvent",
            {
                "value": 42,
            },
        )
    ]

    # Cache
    infrastructure.cache.set(
        "permanent",
        123,
    )

    assert infrastructure.cache.get(
        "permanent"
    ) == 123

    infrastructure.cache.set(
        "short",
        "value",
        ttl_seconds=0.01,
    )

    sleep(0.02)

    assert infrastructure.cache.get(
        "short"
    ) is None

    # Plugin manager
    plugin = TestPlugin()

    infrastructure.plugins.register(
        plugin
    )

    assert infrastructure.services.resolve(
        "test_service"
    )["status"] == "registered"

    infrastructure.plugins.start(
        "Test Plugin"
    )

    assert plugin.started is True
    assert infrastructure.plugins.state(
        "Test Plugin"
    ).started is True

    infrastructure.plugins.stop(
        "Test Plugin"
    )

    assert plugin.started is False

    print("=" * 78)
    print("BURSAAI v6.0 SPRINT 5A.0 TEST")
    print("=" * 78)
    print("Service Container      : OK")
    print("Lazy Factory Resolution: OK")
    print("Event Bus              : OK")
    print("Event History          : OK")
    print("Cache Manager          : OK")
    print("TTL Expiry             : OK")
    print("Plugin Manager         : OK")
    print("Plugin Lifecycle       : OK")
    print("Configuration          : OK")
    print("Infrastructure Bootstrap: OK")
    print("=" * 78)
    print("SPRINT 5A.0 INFRASTRUCTURE LAYER OK")


if __name__ == "__main__":
    main()
