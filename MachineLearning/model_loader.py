from __future__ import annotations
import json
from pathlib import Path
import joblib
from MachineLearning.simple_models import MeanThresholdClassifier
from MachineLearning.sklearn_models import SklearnClassifierModel

class DeploymentModelLoader:
    def load(self, entry):
        path=Path(entry['model_path'])
        if not path.exists(): raise FileNotFoundError(path)
        if path.suffix=='.joblib':
            estimator=joblib.load(path); model=SklearnClassifierModel(estimator,entry.get('model_name') or path.stem); model.is_fitted=True; model.metadata.model_id=entry['model_id']; model.metadata.feature_names=list(entry.get('feature_names',[])); return model
        payload=json.loads(path.read_text(encoding='utf-8')); model=MeanThresholdClassifier(entry.get('model_name') or 'Mean Threshold'); model.load_state(payload['state']); model.metadata.model_id=entry['model_id']; model.metadata.feature_names=list(entry.get('feature_names',[])); return model
