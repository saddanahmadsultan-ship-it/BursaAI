from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional
@dataclass
class PredictionResult:
    prediction:float; probability:Optional[float]=None; confidence:Optional[float]=None; model_id:str=""; metadata:Dict[str,Any]|None=None
    def to_dict(self): return asdict(self)
