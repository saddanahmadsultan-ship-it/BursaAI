BursaAI v6.0 Professional Framework
Sprint 4A - Base Adapter + Legacy Bridge

NEW FILES
---------
Adapters/__init__.py
Adapters/base_adapter.py
Framework/legacy_bridge.py
Tests/test_sprint4a.py

UPDATED
-------
Framework/__init__.py

PURPOSE
-------
LegacyBridge translates both directions:

Legacy dict
    ⇄
AnalysisContext / AnalysisModel

BaseAdapter standardizes wrappers for existing Core functions.

INSTALLATION
------------
Extract into the BursaAI project root.
Merge Framework, Adapters and Tests folders.

DO NOT modify:
- main.py
- Core/
- existing trading engines

TESTS
-----
From BursaAI root:

python -c "from Framework.legacy_bridge import LegacyBridge; print('LEGACY BRIDGE OK')"
python -c "from Adapters.base_adapter import BaseAdapter; print('BASE ADAPTER OK')"
python Tests/test_sprint4a.py

From Tests folder:

python test_sprint4a.py
