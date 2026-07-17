BursaAI v7 Sprint 7C.1 Release Pack
Institutional Position Intelligence Engine

IMPORTANT

This pack is built on the last validated Sprint 7B.4 Release Pack.

INSTALL

1. Merge Sprint 7B.4 into develop.
2. Run:

   git switch develop
   git pull origin develop
   git switch -c feature/7c1-position-intelligence

3. Extract this ZIP.
4. Copy all content into the BursaAI project root.
5. Select Replace/Merge.

VALIDATION

python -m unittest Tests.test_sprint7c1 -v
python main_v7_position_intelligence.py
python Tools\repository_cleanup_audit.py
python Tools\pre_commit_security_check.py

EXPECTED

Ran 8 tests
OK

SPRINT 7C.1 COMPLETED

GIT

git add .
git commit -m "feat(trading): add Sprint 7C.1 institutional position intelligence"
git push -u origin feature/7c1-position-intelligence

Open Pull Request:

base: develop
compare: feature/7c1-position-intelligence

RUNTIME OUTPUTS

Reports/PositionIntelligence/

These generated files are ignored by Git.
