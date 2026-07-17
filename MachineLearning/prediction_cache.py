from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Any, Dict, Optional

class PredictionCache:
    def __init__(self, path='Models/prediction_cache.json'):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True); self.data=self._load()
    def _load(self):
        if not self.path.exists(): return {}
        try: return json.loads(self.path.read_text(encoding='utf-8'))
        except (json.JSONDecodeError,OSError): return {}
    @staticmethod
    def key(candidate_id: str, features: Dict[str,float], model_ids):
        raw=json.dumps({'candidate_id':candidate_id,'features':features,'models':sorted(model_ids)},sort_keys=True,separators=(',',':'))
        return hashlib.sha256(raw.encode()).hexdigest()
    def get(self,key)->Optional[Dict[str,Any]]: return self.data.get(key)
    def set(self,key,value):
        self.data[key]=value
        tmp=self.path.with_suffix('.tmp'); tmp.write_text(json.dumps(self.data,indent=2,sort_keys=True),encoding='utf-8'); tmp.replace(self.path)
