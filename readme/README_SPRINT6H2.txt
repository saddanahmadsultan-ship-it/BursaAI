BursaAI v6.0.0 RC1
Sprint 6H.2 - Paper-Trading Soak Test

TEST
----
python Tests/test_sprint6h2.py

SOAK TEST
---------
python Scripts/run_paper_soak.py --iterations 100

LONG SOAK
---------
python Scripts/run_paper_soak.py --iterations 1000

OUTPUT
------
Reports/Release/rc1_paper_soak_report.txt
Reports/Release/rc1_paper_soak_report.json

PASS CONDITIONS
---------------
Failed iterations       = 0
Duplicate orders        = 0
Journal inconsistencies = 0
Cash and equity         >= 0
Peak positions          <= configured maximum
