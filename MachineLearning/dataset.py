from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List
from MachineLearning.feature_schema import FeatureSchema
@dataclass
class MLDatasetSplit: train:"MLDataset"; validation:"MLDataset"; test:"MLDataset"
@dataclass
class MLDataset:
    schema:FeatureSchema; rows:List[Dict[str,float]]; targets:List[float]; metadata:List[Dict[str,Any]]
    def __post_init__(self):
        if len(self.rows)!=len(self.targets): raise ValueError("Rows dan targets mesti sama panjang.")
        if self.metadata and len(self.metadata)!=len(self.rows): raise ValueError("Metadata mesti kosong atau sama panjang.")
    @property
    def size(self): return len(self.rows)
    @property
    def feature_names(self): return self.schema.feature_names
    def as_matrix(self): return [[r[n] for n in self.feature_names] for r in self.rows], list(self.targets)
    def split(self,train_ratio=.70,validation_ratio=.15):
        if not 0<train_ratio<1 or not 0<=validation_ratio<1 or train_ratio+validation_ratio>=1: raise ValueError("Invalid split ratio.")
        a=int(self.size*train_ratio); b=a+int(self.size*validation_ratio)
        def sub(s,e): return MLDataset(self.schema,self.rows[s:e],self.targets[s:e],self.metadata[s:e] if self.metadata else [])
        return MLDatasetSplit(sub(0,a),sub(a,b),sub(b,self.size))
    @classmethod
    def from_records(cls,schema,records:Iterable[Dict[str,Any]]):
        rows=[]; targets=[]; metadata=[]
        for rec in records:
            rows.append(schema.validate_row(rec))
            if schema.target_name not in rec: raise ValueError(f"Missing target: {schema.target_name}")
            targets.append(float(rec[schema.target_name])); metadata.append(dict(rec.get("metadata",{})))
        return cls(schema,rows,targets,metadata)
