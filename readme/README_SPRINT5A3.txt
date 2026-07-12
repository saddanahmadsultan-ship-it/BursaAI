BursaAI v6.0 Professional Framework
Sprint 5A.3 - AI Brain Adapter

NEW FILES
---------
Adapters/ai_brain_adapter.py
Tests/test_sprint5a3.py
Tests/test_sprint5a3_core_imports.py

UPDATED
-------
Adapters/ai_layer_adapters.py
Adapters/__init__.py

LEGACY FUNCTION WRAPPED
-----------------------
Core.ai_brain.apply_ai_brain

CONTEXT OUTPUT
--------------
context.analysis.ai.conviction_score
context.analysis.ai.conviction_level
context.analysis.ai.signal
context.analysis.ai.prediction_stability
context.analysis.ai.execution_quality
context.analysis.ai.strengths
context.analysis.ai.weaknesses
context.analysis.ai.summary
context.analysis.ai.components
context.analysis.ai.contributions
context.metadata["ai_brain_data"]
context.analysis.extra["ai_brain"]

EVENT
-----
AIBrainCompleted

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

python -c "from Adapters.ai_brain_adapter import AIBrainAdapter; print('AI BRAIN ADAPTER OK')"
python Tests/test_sprint5a3.py
python Tests/test_sprint5a3_core_imports.py

The main test uses fake functions and does not require internet access.
