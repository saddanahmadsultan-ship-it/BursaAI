BursaAI v7 Sprint 7B.2 Release Pack
Research Dataset Builder + Feature Engineering

INSTALL

1. Pastikan Sprint 7B.1 sudah merge ke develop.
2. Jalankan:

   git switch develop
   git pull origin develop
   git switch -c feature/7b2-research-dataset

3. Extract ZIP.
4. Copy semua kandungan ke root BursaAI.
5. Pilih Replace/Merge.

VALIDATION

python -m unittest Tests.test_sprint7b2 -v
python main_v7_dataset_builder.py
python Tools\repository_cleanup_audit.py
python Tools\pre_commit_security_check.py

EXPECTED

Ran 8 tests
OK

SPRINT 7B.2 COMPLETED

GIT

git add .
git commit -m "feat(ml): add Sprint 7B.2 research dataset and feature engineering"
git push -u origin feature/7b2-research-dataset

Open Pull Request:

base: develop
compare: feature/7b2-research-dataset

GENERATED OUTPUT

Datasets/Research/
  research_ml_dataset.csv
  research_ml_dataset.json
  research_ml_summary.json

The Datasets folder is ignored by Git because it contains generated ML artifacts.
