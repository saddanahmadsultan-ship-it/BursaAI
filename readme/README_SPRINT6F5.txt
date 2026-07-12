BursaAI v6.0 Walk Forward
Sprint 6F.5 - Walk Forward Analyzer

FILES
-----
WalkForward/analyzer_models.py
WalkForward/analyzer_metrics.py
WalkForward/walkforward_analyzer.py
WalkForward/analyzer_report.py
WalkForward/analyzer_services.py
WalkForward/__init__.py
Tests/test_sprint6f5.py

FEATURES
--------
- training vs validation comparison
- out-of-sample degradation
- pass/fail by window
- stability score
- consistency score
- robustness score
- best and worst window
- overall verdict
- warning generation
- event publication
- ServiceContainer registration
- text report

VERDICTS
--------
ROBUST
ACCEPTABLE
WEAK
FAILED

EVENT
-----
WalkForwardAnalysisCompleted

TEST
----
python Tests/test_sprint6f5.py

EXPECTED
--------
SPRINT 6F.5 WALK FORWARD ANALYZER OK
