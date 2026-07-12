BursaAI v6.0 Walk Forward
Sprint 6F.6B - Optimization Engine & Registry

FILES
-----
WalkForward/optimization_models.py
WalkForward/optimization_scoring.py
WalkForward/optimization_engine.py
WalkForward/optimization_registry.py
WalkForward/optimization_services.py
WalkForward/__init__.py
Tests/test_sprint6f6b.py

FEATURES
--------
- candidate evaluation
- metric normalization
- weighted optimization score
- artifact capture
- warning and error capture
- duration profiling
- best candidate selection
- optimizer registry
- ServiceContainer registration
- candidate and run events

DEFAULT SCORE WEIGHTS
---------------------
Robustness      35%
Profit Factor   25%
Sharpe          15%
Drawdown        10%
Win Rate        10%
Stability        5%

EVENTS
------
OptimizationCandidateCompleted
OptimizationRunCompleted

TEST
----
python Tests/test_sprint6f6b.py

EXPECTED
--------
SPRINT 6F.6B OPTIMIZATION ENGINE & REGISTRY OK
