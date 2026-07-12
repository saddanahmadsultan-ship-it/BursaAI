# BursaAI Changelog

## 6.0.0-rc1

### Added

- Professional modular framework and analysis pipeline.
- Legacy adapter layer for existing Core engines.
- Dynamic risk, position sizing and portfolio allocation adapters.
- Unified execution framework.
- Paper Trading Engine.
- Notification Hub and Telegram integration foundation.
- SQLite Trade Journal.
- Performance Analytics.
- Complete Walk Forward framework:
  - historical data builder
  - dataset splitting
  - training runner
  - validation runner
  - walk-forward analyzer
  - parameter optimization
  - final reporting
  - full pipeline integration
- Unified service bootstrap.
- Unified JSON configuration and `main_v6.py`.
- Full regression suite.
- Release backup, rollback and version manifest utilities.
- RC1 preflight, packaging and integrity verification tools.

### Changed

- BursaAI execution is now service-driven rather than controlled by a large legacy `main.py`.
- Portfolio allocation is performed at batch level after individual stock analysis.
- Configuration supports environment-variable overrides.

### Known limitations

- Broker live execution is not included.
- Walk-forward training and validation still require concrete strategy callbacks.
- Telegram credentials must be supplied through environment variables.
- RC1 should be validated using paper trading before any live deployment.
