BursaAI v6.0 Professional Framework
Sprint 5A.2 - Entry Timing Adapter

NEW FILES
---------
Adapters/entry_timing_adapter.py
Tests/test_sprint5a2.py
Tests/test_sprint5a2_core_imports.py

UPDATED
-------
Adapters/ai_layer_adapters.py
Adapters/__init__.py

LEGACY FUNCTION WRAPPED
-----------------------
Core.entry_timing_engine.apply_entry_timing_engine

CONTEXT OUTPUT
--------------
context.analysis.timing.score
context.analysis.timing.status
context.analysis.timing.action
context.analysis.timing.entry_zone_low
context.analysis.timing.entry_zone_high
context.analysis.timing.reasons
context.analysis.timing.warnings
context.metadata["entry_timing_data"]
context.analysis.extra["entry_timing"]

EVENT
-----
EntryTimingCompleted

INSTALLATION
------------
Extract into the BursaAI project root.
Merge Adapters and Tests folders.

DO NOT modify:
- main.py
- Core/
- Framework/

TESTS
-----
From BursaAI root:

python -c "from Adapters.entry_timing_adapter import EntryTimingAdapter; print('ENTRY TIMING ADAPTER OK')"
python Tests/test_sprint5a2.py
python Tests/test_sprint5a2_core_imports.py

The main test uses fake functions and does not require internet access.
