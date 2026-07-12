BursaAI v6.0 Professional Framework
Sprint 5A.1 - Market Regime Adapter

NEW FILES
---------
Adapters/market_regime_adapter.py
Adapters/ai_layer_adapters.py
Tests/test_sprint5a1.py
Tests/test_sprint5a1_core_imports.py

UPDATED
-------
Adapters/__init__.py

LEGACY FUNCTION WRAPPED
-----------------------
Core.market_regime_engine.apply_market_regime_engine

CONTEXT OUTPUT
--------------
context.analysis.market.regime
context.analysis.market.regime_score
context.analysis.score.regime_bonus
context.analysis.score.regime_penalty
context.analysis.score.final
context.metadata["market_regime_data"]
context.analysis.extra["market_regime"]

EVENT
-----
MarketRegimeCompleted

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

python -c "from Adapters.market_regime_adapter import MarketRegimeAdapter; print('MARKET REGIME ADAPTER OK')"
python Tests/test_sprint5a1.py
python Tests/test_sprint5a1_core_imports.py

The main test uses fake functions and does not require internet access.
