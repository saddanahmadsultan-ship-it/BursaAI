BursaAI v6.0 Release Integration
Sprint 6G.1 - Unified Service Bootstrap + Full Import Test

FILES
-----
Bootstrap/__init__.py
Bootstrap/application_services.py
Bootstrap/import_health.py
Bootstrap/service_collision.py
Bootstrap/service_manifest.py
Bootstrap/service_bootstrap.py
Tests/test_all_imports.py
Tests/test_sprint6g1.py

PURPOSE
-------
- initialize one shared InfrastructureBundle
- build the full analysis pipeline
- register portfolio allocation
- register ExecutionManager
- register paper trading
- register Notification Hub
- register Trade Journal
- register Performance Analytics
- detect planned service-name collisions
- run full import health checks
- expose ApplicationServices

TESTS
-----
python Tests/test_all_imports.py
python Tests/test_sprint6g1.py

EXPECTED
--------
SPRINT 6G.1 FULL IMPORT TEST OK
SPRINT 6G.1 UNIFIED SERVICE BOOTSTRAP OK

NOTE
----
Walk Forward registration is intentionally deferred until
Sprint 6G.2 because it requires concrete training, validation,
optimization and window-generator functions.
