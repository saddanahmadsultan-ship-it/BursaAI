BursaAI v6.0 Walk Forward
Sprint 6F.3 - Training Window Runner

FILES
-----
WalkForward/training_models.py
WalkForward/training_runner.py
WalkForward/training_registry.py
WalkForward/training_services.py
WalkForward/training_report.py
Tests/test_sprint6f3.py

FEATURES
--------
- injected training function
- one-window and multi-window training
- parameter, metric and artifact capture
- warning and error capture
- duration profiling
- training registry
- ServiceContainer registration
- event publication

EVENTS
------
TrainingWindowCompleted
TrainingRunCompleted

TEST
----
python Tests/test_sprint6f3.py

EXPECTED
--------
SPRINT 6F.3 TRAINING WINDOW RUNNER OK
