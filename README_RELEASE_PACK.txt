BursaAI v7 Sprint 7A.5 RC1 Release Pack
AI Ranking Core + Weighted Scoring + Leaderboard

INSTALLATION

1. Backup folder BursaAI.
2. Extract ZIP.
3. Copy semua kandungan ke root BursaAI.
4. Pilih Replace/Merge.
5. Jalankan dari root BursaAI:

   python -m unittest Tests.test_sprint7a5_rc1 -v
   python main_v7_ranking.py

Tiada edit sys.path.
Tiada PowerShell script diperlukan.
Tiada susunan fail manual.

OUTPUT

Reports/Ranking/
  leaderboard.csv
  leaderboard.json
  summary.json

RC1 FEATURES

- Multi-factor weighted scoring
- Configurable normalized weights
- Performance score
- Risk score
- Consistency score
- Robustness score
- Confidence score
- Overall AI score
- Tier classification
- Recommendation mapping
- Deterministic ranking
- CSV/JSON export
- Release launcher
- Unit tests

RC1 LIMITATION

Robustness dan consistency menggunakan metrik yang telah tersedia.
Formula lanjutan berdasarkan fold, monthly return, regime dan parameter stability
akan dibina dalam RC2 dan RC3.
