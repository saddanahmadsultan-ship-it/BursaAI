# BursaAI v6.0.0 RC1

BursaAI v6 RC1 is the first release candidate of the modular BursaAI platform.

## Release objective

This release consolidates the completed v6 architecture into a testable release candidate suitable for:

- full regression testing
- paper trading
- portfolio simulation
- walk-forward research
- release health validation
- controlled backup and rollback

## Recommended use

Use RC1 for paper trading and research only. Do not connect this release to a live broker until the release regression suite, health checks and paper-trading validation have all passed.

## Required checks

Run these commands from the project root:

```powershell
python Tests\test_release_imports.py
python Tests\run_release_regression.py
python Tests\test_sprint6h_rc1.py
python Scripts\rc1_preflight.py
```

## Release status

```text
Version : 6.0.0-rc1
Channel : Release Candidate
Live Trading Approval : NO
Paper Trading Approval: YES, after tests pass
```
