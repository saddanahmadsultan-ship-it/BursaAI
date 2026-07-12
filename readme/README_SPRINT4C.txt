BursaAI v6.0 Professional Framework
Sprint 4C - Score, Trend and Momentum Adapters

NEW FILES
---------
Adapters/score_adapter.py
Adapters/trend_adapter.py
Adapters/momentum_adapter.py
Adapters/analysis_adapters.py
Tests/test_sprint4c.py
Tests/test_sprint4c_core_imports.py

UPDATED
-------
Adapters/__init__.py

LEGACY FUNCTIONS WRAPPED
------------------------
Core.scorer.calculate_score
Core.trend_engine.score_trend
Core.momentum_engine.score_momentum

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

python -c "from Adapters.score_adapter import ScoreAdapter; print('SCORE ADAPTER OK')"
python -c "from Adapters.trend_adapter import TrendAdapter; print('TREND ADAPTER OK')"
python -c "from Adapters.momentum_adapter import MomentumAdapter; print('MOMENTUM ADAPTER OK')"

python Tests/test_sprint4c.py
python Tests/test_sprint4c_core_imports.py

The main test uses fake functions and does not require internet access.
