BursaAI v7 Sprint 7B.3 Release Pack
Model Training, Evaluation & Model Selection

INSTALL
1. git switch develop
2. git pull origin develop
3. git switch -c feature/7b3-model-training
4. Extract ZIP and copy all files to BursaAI root.
5. python -m pip install -r requirements.txt
6. python -m unittest Tests.test_sprint7b3 -v
7. python main_v7_model_training.py

GIT
git add .
git commit -m "feat(ml): add Sprint 7B.3 model training evaluation and selection"
git push -u origin feature/7b3-model-training

Pull Request: base develop, compare feature/7b3-model-training
