BursaAI v6.0 Release Integration
Sprint 6G.4 - Full Regression Suite + Release Dry Run

FILES
-----
Bootstrap/regression_models.py
Bootstrap/regression_suite.py
Bootstrap/release_dry_run.py
Bootstrap/regression_report.py
Bootstrap/regression_services.py
Bootstrap/__init__.py
Tests/test_sprint6g4.py
Tests/run_release_regression.py

TEST
----
python Tests/test_sprint6g4.py

FULL RELEASE REGRESSION
-----------------------
python Tests/run_release_regression.py

OUTPUT
------
Reports/Release/regression_report.txt
Reports/Release/regression_report.json

EXPECTED
--------
SPRINT 6G.4 FULL REGRESSION SUITE OK
