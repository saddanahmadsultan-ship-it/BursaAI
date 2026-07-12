BursaAI v6.0 Walk Forward
Sprint 6F.2B - Dataset Splitter

FILES
-----
WalkForward/training_dataset.py
WalkForward/validation_dataset.py
WalkForward/dataset_splitter.py
WalkForward/split_validator.py
WalkForward/dataset_split_services.py
WalkForward/__init__.py
Tests/test_sprint6f2b.py

FEATURES
--------
- training dataset model
- validation dataset model
- rolling window split
- expanding window split
- multiple window split
- minimum row validation
- look-ahead leakage prevention
- validation ordering checks
- defensive DataFrame copying
- ServiceContainer registration

TEST
----
python Tests/test_sprint6f2b.py

EXPECTED
--------
SPRINT 6F.2B DATASET SPLITTER OK
