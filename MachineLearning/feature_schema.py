from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List
@dataclass(frozen=True)
class FeatureDefinition:
    name:str; dtype:str="float"; required:bool=True; default:float=0.0; description:str=""
    def to_dict(self)->Dict[str,Any]: return asdict(self)
@dataclass
class FeatureSchema:
    features:List[FeatureDefinition]=field(default_factory=list); target_name:str="target"
    def __post_init__(self):
        names=[f.name for f in self.features]
        if len(names)!=len(set(names)): raise ValueError("Feature names mesti unik.")
        if self.target_name in names: raise ValueError("Target name tidak boleh menjadi feature.")
    @property
    def feature_names(self): return [f.name for f in self.features]
    def validate_row(self,row):
        out={}
        for f in self.features:
            if f.name not in row:
                if f.required: raise ValueError(f"Missing required feature: {f.name}")
                value=f.default
            else: value=row[f.name]
            try: out[f.name]=float(value)
            except (TypeError,ValueError) as e: raise ValueError(f"Feature {f.name} mesti numeric.") from e
        return out
    def to_dict(self): return {"target_name":self.target_name,"features":[f.to_dict() for f in self.features]}
    @classmethod
    def from_names(cls,names:Iterable[str],target_name="target"): return cls([FeatureDefinition(n) for n in names],target_name)
