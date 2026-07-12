BursaAI v6.0 Sprint 5C.1 - Dynamic Risk Adapter

Files:
Adapters/dynamic_risk_adapter.py
Adapters/execution_adapters.py
Adapters/full_pipeline_registry.py
Adapters/__init__.py
Tests/test_sprint5c1.py
Tests/test_sprint5c1_core_imports.py

Event:
DynamicRiskCalculated

Tests:
python -c "from Adapters.dynamic_risk_adapter import DynamicRiskAdapter; print('DYNAMIC RISK ADAPTER OK')"
python Tests/test_sprint5c1.py
python Tests/test_sprint5c1_core_imports.py
