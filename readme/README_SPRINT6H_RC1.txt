BursaAI v6.0.0 Release Candidate 1
Sprint 6H

FILES
-----
VERSION
CHANGELOG.md
RELEASE_NOTES.md

Release/
- __init__.py
- release_manifest.py
- integrity.py
- preflight.py
- rc_builder.py

Scripts/
- rc1_preflight.py
- build_rc1.py
- verify_rc1.py

Tests/
- test_sprint6h_rc1.py

TEST
----
python Tests/test_sprint6h_rc1.py

PROJECT PREFLIGHT
-----------------
python Scripts/rc1_preflight.py

BUILD RC1
---------
python Scripts/build_rc1.py

VERIFY PROJECT AGAINST MANIFEST
-------------------------------
python Scripts/verify_rc1.py

BUILD OUTPUT
------------
Dist/BursaAI_v6.0.0_rc1.zip
Dist/BursaAI_v6.0.0_rc1_manifest.json
