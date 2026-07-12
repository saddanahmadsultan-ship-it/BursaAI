BursaAI v7 Sprint 7A.5 RC4 Release Pack
Pareto Ranking + Confidence Engine + Tier Gate

INSTALL

1. Pastikan RC3 sudah merge ke develop.
2. Jalankan:

   git switch develop
   git pull
   git switch -c feature/7a5-rc4-pareto-confidence

3. Extract ZIP.
4. Copy semua kandungan ke root BursaAI.
5. Pilih Replace/Merge.
6. Jalankan:

   python -m unittest Tests.test_sprint7a5_rc4 -v
   python main_v7_pareto.py

SELEPAS LULUS

git add .
git commit -m "feat(research): add Sprint 7A.5 RC4 pareto confidence tier gate"
git push -u origin feature/7a5-rc4-pareto-confidence

RC4 FEATURES

- Non-dominated Pareto sorting
- Pareto fronts
- Crowding distance
- Confidence Engine v2
- Data coverage score
- Fold quality score
- Trade sample score
- Regime coverage score
- Stability alignment score
- Out-of-sample quality score
- Tier Gate
- Promotion Engine
- Pareto and promotion reports
- AI Ranking integration

OUTPUT

Reports/Ranking/
  leaderboard.csv
  leaderboard.json
  summary.json

Reports/Pareto/
  pareto_front.csv
  pareto_front.json
  promotion_report.json
