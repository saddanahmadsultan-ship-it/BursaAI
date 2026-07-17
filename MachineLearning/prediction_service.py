from __future__ import annotations
from pathlib import Path
from MachineLearning.active_model_registry import ActiveModelRegistry
from MachineLearning.confidence_calibrator import ConfidenceCalibrator
from MachineLearning.ensemble_predictor import EnsemblePredictor
from MachineLearning.feature_engineering import ResearchFeatureEngineer
from MachineLearning.model_loader import DeploymentModelLoader
from MachineLearning.prediction_cache import PredictionCache
from MachineLearning.prediction_contracts import PromotionPrediction
from MachineLearning.promotion_classifier import MLPromotionClassifier

class MLPredictionService:
    def __init__(self, model_dir='Models/Sprint7B4', include_challengers=False, cache_path=None):
        self.registry=ActiveModelRegistry(model_dir); self.entries=self.registry.active_entries(include_challengers); loader=DeploymentModelLoader(); self.models=[loader.load(e) for e in self.entries]; self.engineer=ResearchFeatureEngineer(); self.ensemble=EnsemblePredictor(); self.calibrator=ConfidenceCalibrator(); self.classifier=MLPromotionClassifier(); self.cache=PredictionCache(cache_path or Path(model_dir)/'prediction_cache.json')
    def predict(self, candidate_id, raw_features, metadata=None):
        engineered=self.engineer.transform(raw_features); feature_names=self.entries[0].get('feature_names') or list(engineered.keys()); vector=[float(engineered.get(name,0.0)) for name in feature_names]; model_ids=[m.metadata.model_id for m in self.models]; key=self.cache.key(str(candidate_id),engineered,model_ids); cached=self.cache.get(key)
        if cached:
            cached['cache_hit']=True; return PromotionPrediction(**cached)
        result=self.ensemble.predict(self.models,vector); calibrated=self.calibrator.calibrate(result['probability']); confidence=self.calibrator.confidence(calibrated); decision,reason=self.classifier.classify(calibrated,confidence)
        prediction=PromotionPrediction(str(candidate_id),result['probability'],calibrated,confidence,result['predicted_class'],decision,reason,result['model_ids'],self.entries[0].get('model_name',''),False,metadata=metadata or {})
        payload=prediction.to_dict(); payload['cache_hit']=False; self.cache.set(key,payload); return prediction
