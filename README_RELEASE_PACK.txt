BursaAI v7 Sprint 7A.5 RC3 Release Pack
Consistency Engine

INSTALL

1. Pastikan RC2 sudah digabungkan ke develop.
2. Jalankan:

   git switch develop
   git pull
   git switch -c feature/7a5-rc3-consistency

3. Extract ZIP.
4. Copy semua kandungan ke root BursaAI.
5. Pilih Replace/Merge.
6. Jalankan:

   python -m unittest Tests.test_sprint7a5_rc3 -v
   python main_v7_consistency.py

SELEPAS LULUS

git add .
git commit -m "feat(research): add Sprint 7A.5 RC3 consistency engine"
git push -u origin feature/7a5-rc3-consistency

RC3 FEATURES

- Walk Forward fold consistency
- Monthly return stability
- Yearly return stability
- Equity curve smoothness
- Return reliability score
- Overall consistency score
- AI Ranking Engine integration
- Leaderboard consistency columns
- CSV and JSON export
- RC3 unit test suite

OUTPUT

Reports/Ranking/
  leaderboard.csv
  leaderboard.json
  summary.json
