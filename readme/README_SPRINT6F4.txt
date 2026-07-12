BursaAI v6.0 Walk Forward
Sprint 6F.4 - Validation Window Runner

FILES
-----
WalkForward/validation_models.py
WalkForward/validation_runner.py
WalkForward/validation_registry.py
WalkForward/validation_services.py
WalkForward/validation_report.py
WalkForward/__init__.py
Tests/test_sprint6f4.py

FEATURES
--------
- out-of-sample validation
- training parameter reuse
- single-window validation
- multi-window validation
- metric capture
- prediction capture
- artifact capture
- warnings and errors
- duration profiling
- validation registry
- ServiceContainer registration
- event publication
- text report

EVENTS
------
ValidationWindowCompleted
ValidationRunCompleted

TEST
----
python Tests/test_sprint6f4.py

EXPECTED
--------
SPRINT 6F.4 VALIDATION WINDOW RUNNER OK
