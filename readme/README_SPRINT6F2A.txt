BursaAI v6.0 Walk Forward
Sprint 6F.2A - Historical Dataset Builder

FILES
-----
WalkForward/__init__.py
WalkForward/dataframe_validator.py
WalkForward/history_loader.py
WalkForward/dataset_cache.py
WalkForward/dataset_builder.py
WalkForward/dataset_services.py
Tests/test_sprint6f2a.py

FEATURES
--------
- Core data loader wrapper
- OHLCV column normalization
- Datetime index normalization
- duplicate timestamp removal
- ascending sort
- numeric conversion
- invalid OHLCV validation
- minimum history validation
- missing business-day detection
- in-memory defensive-copy cache
- ServiceContainer registration

TEST
----
python Tests/test_sprint6f2a.py

EXPECTED
--------
SPRINT 6F.2A HISTORICAL DATASET BUILDER OK
