BursaAI v7 Sprint 7A.5 RC2 Release Pack
Robustness Engine

INSTALL

1. Backup BursaAI.
2. Extract ZIP.
3. Copy semua kandungan ke root BursaAI.
4. Pilih Replace/Merge.
5. Jalankan:

   python -m unittest Tests.test_sprint7a5_rc2 -v
   python main_v7_robustness.py

GIT WORKFLOW

git switch develop
git switch -c feature/7a5-rc2-robustness

Selepas copy dan test:

git add .
git commit -m "feat(research): add Sprint 7A.5 RC2 robustness engine"
git push -u origin feature/7a5-rc2-robustness

RC2 FEATURES

- Walk Forward fold success score
- Train-test degradation score
- Fold dispersion score
- Parameter stability score
- Regime stability score
- Overall robustness score
- AI Ranking Engine integration
- Leaderboard robustness columns
- CSV and JSON robustness export
- RC2 unit test suite

LIMITATION

Parameter stability RC2 menggunakan jarak parameter antara candidate.
Neighborhood performance surface analysis akan dipertingkatkan dalam RC berikutnya.
