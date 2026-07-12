# BursaAI v6.0.0 RC1 Final Release Gate

Run these commands from the BursaAI project root.

```powershell
python Tests\run_release_regression.py
python Scripts\smoke_test_rc1.py
python Scripts\validate_rc1.py
python Scripts\run_paper_soak.py --iterations 1000
python Scripts\build_rc1.py
python Scripts\verify_rc1.py
python Scripts\run_final_release_gate.py
```

## Approval rules

The release gate returns:

- `APPROVED`
- `CONDITIONAL`
- `REJECTED`

Mandatory evidence:

- regression passed
- RC validation passed
- paper-trading soak passed
- correct version file

Recommended evidence:

- release manifest available and valid

## Scope of approval

`APPROVED` means approved for extended paper trading and controlled research.

It does not approve live broker execution.
