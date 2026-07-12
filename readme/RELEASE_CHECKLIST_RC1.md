# BursaAI v6.0.0 RC1 Release Checklist

Complete these checks from the BursaAI project root.

## Required

```powershell
python Tests\test_all_imports.py
python Tests\test_release_imports.py
python Tests\run_release_regression.py
python Tests\test_sprint6h_rc1.py
python Tests\test_sprint6h1.py
python Scripts\rc1_preflight.py
python Scripts\smoke_test_rc1.py
python Scripts\validate_rc1.py
python Scripts\build_rc1.py
python Scripts\verify_rc1.py
```

## Approval rule

RC1 is ready for extended paper trading only when every command exits successfully.

## Not approved

Do not use RC1 for live broker execution.
