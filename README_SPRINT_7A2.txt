BursaAI Sprint 7A.2 - Experiment Registry + Persistent Checkpoint

PASANG:
1. Backup folder BursaAI.
2. Extract ZIP.
3. Copy semua kandungan ke root BursaAI dan pilih Replace/Merge.
4. Jalankan:
   python -c "from Research import ExperimentRegistry; print('SPRINT 7A.2 IMPORT OK')"
   python Tests\test_sprint7a2.py
   python Tools\demo_sprint7a2.py

FUNGSI: register, save, load, list, pause, resume, cancel, recover, checkpoint, rebuild_manifest, delete.
Checkpoint atomik menggunakan SHA256. Recovery RUNNING ditukar kepada PAUSED untuk keselamatan.
