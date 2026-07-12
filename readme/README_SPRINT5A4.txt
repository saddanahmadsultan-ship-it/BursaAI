BursaAI v6.0 Professional Framework
Sprint 5A.4 - AI Layer Registry + Full Integration Test

NEW FILES
---------
Adapters/full_pipeline_registry.py
Framework/event_audit.py
Framework/full_pipeline.py
Tests/test_sprint5a4.py
Tests/test_sprint5a4_real_registry.py

UPDATED
-------
Adapters/__init__.py
Framework/__init__.py

COMPLETE PIPELINE
-----------------
Loader Adapter
Indicator Adapter
Score Adapter
Trend Adapter
Momentum Adapter
Volume Adapter
Quality Gate Adapter
Smart Money Adapter
Market Regime Adapter
Entry Timing Adapter
AI Brain Adapter

FEATURES
--------
- One-call full adapter registration
- Full pipeline factory
- Event audit trail
- Logger and profiler integration
- Service container binding
- Complete fake-data integration test
- Real Core registration smoke test

INSTALLATION
------------
Extract into the BursaAI project root.
Merge Adapters, Framework and Tests folders.

DO NOT modify:
- main.py
- Core/

TESTS
-----
From BursaAI root:

python -c "from Adapters.full_pipeline_registry import register_full_analysis_pipeline; print('FULL REGISTRY OK')"
python -c "from Framework.full_pipeline import build_full_pipeline; print('FULL PIPELINE OK')"
python -c "from Framework.event_audit import EventAuditTrail; print('EVENT AUDIT OK')"

python Tests/test_sprint5a4.py
python Tests/test_sprint5a4_real_registry.py

The full integration test uses fake data and does not require internet access.
The real registry test imports real Core modules but does not execute market downloads.
