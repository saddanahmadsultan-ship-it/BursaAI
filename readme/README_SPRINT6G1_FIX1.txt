BursaAI v6.0 Sprint 6G.1 Fix 1

PROBLEM
-------
Circular import chain:

Adapters.portfolio_allocator_adapter
-> Framework.context
-> Framework/__init__.py
-> Framework.execution_manager
-> Adapters.portfolio_allocator_adapter

FIX
---
1. Framework/__init__.py is now lightweight.
2. Adapters/__init__.py is now lightweight.
3. Bootstrap/__init__.py uses lazy imports.

INSTALL
-------
Replace these files:

Framework/__init__.py
Adapters/__init__.py
Bootstrap/__init__.py

TEST
----
python Tests/test_sprint6g1_fix1.py
python Tests/test_all_imports.py
python Tests/test_sprint6g1.py

EXPECTED
--------
SPRINT 6G.1 CIRCULAR IMPORT FIX OK
SPRINT 6G.1 FULL IMPORT TEST OK
SPRINT 6G.1 UNIFIED SERVICE BOOTSTRAP OK
