BursaAI v6.0 Sprint 6G.5 Fix 1

CAUSE
-----
Tests/test_sprint6g5.py did not add the BursaAI project root
to sys.path before importing Bootstrap.

FIX
---
The corrected test now uses:

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

INSTALL
-------
Replace:
Tests/test_sprint6g5.py

TEST
----
python Tests/test_sprint6g5.py
