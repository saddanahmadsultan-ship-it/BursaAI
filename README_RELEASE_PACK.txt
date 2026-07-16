BursaAI v7 Sprint 7A.5 Final RC Release Pack

INSTALL

1. Pastikan RC4 sudah merge ke develop.
2. Jalankan:

   git switch develop
   git pull
   git switch -c release/7a5-final-rc

3. Extract ZIP.
4. Copy semua kandungan ke root BursaAI.
5. Pilih Replace/Merge.

VALIDATION

python Tests\run_sprint7a5_full_regression.py
python main_v7_final_rc.py
python Tools\repository_cleanup_audit.py
python Tools\pre_commit_security_check.py

EXPECTED

SPRINT 7A.5 FULL REGRESSION PASSED
SPRINT 7A.5 FINAL RC — RELEASE GATE PASSED

GIT

git add .
git commit -m "release(research): prepare Sprint 7A.5 Final RC"
git push -u origin release/7a5-final-rc

Then open Pull Request:

release/7a5-final-rc -> develop
