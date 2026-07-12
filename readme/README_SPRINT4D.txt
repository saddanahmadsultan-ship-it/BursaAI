BursaAI v6.0 Professional Framework
Sprint 4D - Volume, Quality Gate and Smart Money Adapters

NEW FILES
---------
Adapters/volume_adapter.py
Adapters/quality_gate_adapter.py
Adapters/smart_money_adapter.py
Adapters/institutional_adapters.py
Tests/test_sprint4d.py
Tests/test_sprint4d_core_imports.py

UPDATED
-------
Adapters/__init__.py

LEGACY FUNCTIONS WRAPPED
------------------------
Core.volume_engine.score_volume
Core.quality_gate.apply_quality_gate
Core.smart_money_engine.apply_smart_money_engine

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

python -c "from Adapters.volume_adapter import VolumeAdapter; print('VOLUME ADAPTER OK')"
python -c "from Adapters.quality_gate_adapter import QualityGateAdapter; print('QUALITY ADAPTER OK')"
python -c "from Adapters.smart_money_adapter import SmartMoneyAdapter; print('SMART MONEY ADAPTER OK')"

python Tests/test_sprint4d.py
python Tests/test_sprint4d_core_imports.py

The main test uses fake functions and does not require internet access.
