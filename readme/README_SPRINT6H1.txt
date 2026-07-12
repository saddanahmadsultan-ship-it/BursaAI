BursaAI v6.0.0 RC1
Sprint 6H.1 - RC1 Validation & Smoke Test

FILES
-----
Release/rc_validation_models.py
Release/rc_validator.py
Release/rc_validation_report.py
Release/smoke_test.py
Release/__init__.py

Scripts/validate_rc1.py
Scripts/smoke_test_rc1.py

Tests/test_sprint6h1.py
RELEASE_CHECKLIST_RC1.md

TEST
----
python Tests/test_sprint6h1.py

SMOKE TEST
----------
python Scripts/smoke_test_rc1.py

FULL RC VALIDATION
------------------
python Scripts/validate_rc1.py

OUTPUT
------
Reports/Release/rc1_validation_report.txt
Reports/Release/rc1_validation_report.json
