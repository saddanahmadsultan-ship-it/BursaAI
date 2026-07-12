BursaAI v6.0 Professional Framework
Sprint 5A.0 - Infrastructure Layer

NEW FILES
---------
Framework/service_container.py
Framework/event_bus.py
Framework/cache.py
Framework/plugin_manager.py
Framework/configuration.py
Framework/infrastructure.py
Tests/test_sprint5a0.py

UPDATED
-------
Framework/__init__.py

FEATURES
--------
- Dependency injection via ServiceContainer
- Synchronous event publishing/subscription
- In-memory TTL cache
- Plugin registration and lifecycle
- Central framework configuration
- Infrastructure bootstrap bundle

INSTALLATION
------------
Extract into the BursaAI project root.
Merge Framework and Tests folders.

DO NOT modify:
- main.py
- Core/
- Adapters/

TESTS
-----
From BursaAI root:

python -c "from Framework.service_container import ServiceContainer; print('SERVICE CONTAINER OK')"
python -c "from Framework.event_bus import EventBus; print('EVENT BUS OK')"
python -c "from Framework.cache import CacheManager; print('CACHE OK')"
python -c "from Framework.plugin_manager import PluginManager; print('PLUGIN MANAGER OK')"
python -c "from Framework.infrastructure import build_infrastructure; print('INFRASTRUCTURE OK')"

python Tests/test_sprint5a0.py
