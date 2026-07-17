from MachineLearning.model_base import BaseMLModel
from MachineLearning.prediction import PredictionResult
class SklearnClassifierModel(BaseMLModel):
    def __init__(self,estimator,model_name): super().__init__(model_name); self.estimator=estimator
    def fit(self,X,y):
        if not X: raise ValueError('Training matrix kosong.')
        self.estimator.fit(X,y); self.is_fitted=True
    def predict_one(self,row):
        if not self.is_fitted: raise RuntimeError('Model belum dilatih.')
        pred=float(self.estimator.predict([row])[0]); prob=None
        if hasattr(self.estimator,'predict_proba'): prob=float(self.estimator.predict_proba([row])[0][-1])
        return PredictionResult(prediction=pred, probability=round(prob,6) if prob is not None else None, confidence=round(abs(prob-.5)*2,6) if prob is not None else None, model_id=self.metadata.model_id)
    def to_state(self): raise NotImplementedError
    def load_state(self,state): raise NotImplementedError
