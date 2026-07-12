BursaAI Sprint 7A.3 — Batch Experiment Runner

Pasang:
1. Backup BursaAI.
2. Extract ZIP.
3. Copy semua kandungan ke root BursaAI dan pilih Replace/Merge.
4. Jalankan:
   python -c "from Research import ExperimentRunner, RunnerConfig; print('SPRINT 7A.3 IMPORT OK')"
   python Tests\test_sprint7a3.py
   python Tools\demo_sprint7a3.py

Fungsi:
- Sequential dan parallel execution
- Retry dan fail-fast
- Resume candidate belum selesai
- Skip candidate completed
- Auto-checkpoint
- Runner statistics
- Persist progress ke registry
