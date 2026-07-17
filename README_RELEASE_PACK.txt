BursaAI v7 Sprint 7B.4 Release Pack
ML Prediction Service + Research Promotion Integration

INSTALL
1. Merge Sprint 7B.3 into develop.
2. git switch develop
   git pull origin develop
   git switch -c feature/7b4-prediction-service
3. Extract this ZIP and copy all contents into the BursaAI root.
4. python -m pip install -r requirements.txt
5. python -m unittest Tests.test_sprint7b4 -v
6. python main_v7_prediction_service.py

EXPECTED
Ran 8 tests
OK
SPRINT 7B.4 COMPLETED

GIT
git add .
git commit -m "feat(ml): add Sprint 7B.4 prediction service and promotion integration"
git push -u origin feature/7b4-prediction-service

Generated Models, Datasets, Reports, Experiments and ResearchResults remain ignored by Git.
