from __future__ import annotations
from MachineLearning.prediction_service import MLPredictionService

class PredictionAPI:
    def __init__(self, model_dir='Models/Sprint7B4'): self.service=MLPredictionService(model_dir)
    def predict(self, candidate_id, features, metadata=None): return self.service.predict(candidate_id,features,metadata).to_dict()
