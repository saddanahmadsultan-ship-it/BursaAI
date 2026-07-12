BursaAI v6.0 Release Integration
Sprint 6G.3 - main_v6.py + Unified Configuration

FILES
-----
Config/__init__.py
Config/app_config.py
Config/config_loader.py
Config/default_config.json
Bootstrap/application_runner.py
main_v6.py
Tests/test_sprint6g3_config.py
Tests/test_sprint6g3_runner.py

FEATURES
--------
- one unified entry point
- JSON configuration
- environment variable overrides
- analysis mode
- paper mode
- walk-forward mode
- health mode
- result JSON output
- centralized feature flags
- centralized capital and notification settings

TESTS
-----
python Tests/test_sprint6g3_config.py
python Tests/test_sprint6g3_runner.py

RUN
---
python main_v6.py --config Config/default_config.json

ENVIRONMENT EXAMPLES
--------------------
$env:BURSAAI_MODE="analysis"
$env:BURSAAI_SYMBOLS="1155.KL,1023.KL"
$env:BURSAAI_STARTING_CAPITAL="100000"
$env:BURSAAI_TELEGRAM_ENABLED="false"
