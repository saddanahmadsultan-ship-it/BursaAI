from __future__ import annotations
from abc import ABC,abstractmethod
from dataclasses import asdict,dataclass,field
from datetime import datetime,timezone
from typing import Any,Dict,List
from uuid import uuid4
from MachineLearning.prediction import PredictionResult
@dataclass
class ModelMetadata:
    model_id:str; model_name:str; model_version:str; model_type:str; created_at:str; feature_names:List[str]=field(default_factory=list); metrics:Dict[str,float]=field(default_factory=dict); parameters:Dict[str,Any]=field(default_factory=dict)
    def to_dict(self): return asdict(self)
class BaseMLModel(ABC):
    def __init__(self,model_name,model_version="1.0.0"):
        self.metadata=ModelMetadata(f"MLM-{uuid4().hex[:12].upper()}",model_name,model_version,self.__class__.__name__,datetime.now(timezone.utc).isoformat()); self.is_fitted=False
    @abstractmethod
    def fit(self,X,y): ...
    @abstractmethod
    def predict_one(self,row)->PredictionResult: ...
    def predict(self,X):
        if not self.is_fitted: raise RuntimeError("Model belum dilatih.")
        return [self.predict_one(r) for r in X]
    @abstractmethod
    def to_state(self): ...
    @abstractmethod
    def load_state(self,state): ...
