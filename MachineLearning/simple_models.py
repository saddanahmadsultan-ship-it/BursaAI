from statistics import mean
from MachineLearning.model_base import BaseMLModel
from MachineLearning.prediction import PredictionResult
class MeanThresholdClassifier(BaseMLModel):
    def __init__(self,model_name="MeanThresholdClassifier"):
        super().__init__(model_name); self.threshold=0.0; self.feature_weights=[]
    def fit(self,X,y):
        if not X or len(X)!=len(y): raise ValueError("Invalid training data.")
        n=len(X[0]); pos=[r for r,t in zip(X,y) if t>=.5]; neg=[r for r,t in zip(X,y) if t<.5]
        self.feature_weights=[(mean(r[i] for r in pos) if pos else 0)-(mean(r[i] for r in neg) if neg else 0) for i in range(n)]
        scores=[self._score(r) for r in X]; ps=[s for s,t in zip(scores,y) if t>=.5]; ns=[s for s,t in zip(scores,y) if t<.5]
        self.threshold=((mean(ps) if ps else max(scores))+(mean(ns) if ns else min(scores)))/2; self.is_fitted=True
    def _score(self,row): return sum(v*w for v,w in zip(row,self.feature_weights)) if self.feature_weights else mean(row)
    def predict_one(self,row):
        if not self.is_fitted: raise RuntimeError("Model belum dilatih.")
        s=self._score(row); m=max(-60.0,min(60.0,s-self.threshold)); p=1/(1+pow(2.718281828,-m)); pred=1.0 if s>=self.threshold else 0.0
        return PredictionResult(pred,round(p,6),round(abs(p-.5)*2,6),self.metadata.model_id,{"raw_score":s,"threshold":self.threshold})
    def to_state(self): return {"threshold":self.threshold,"feature_weights":self.feature_weights,"metadata":self.metadata.to_dict(),"is_fitted":self.is_fitted}
    def load_state(self,state): self.threshold=float(state.get("threshold",0)); self.feature_weights=[float(v) for v in state.get("feature_weights",[])]; self.is_fitted=bool(state.get("is_fitted",False))
