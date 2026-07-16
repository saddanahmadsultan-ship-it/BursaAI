import json
from pathlib import Path
from MachineLearning.simple_models import MeanThresholdClassifier
class MLModelRegistry:
    def __init__(self,root_dir="Models"): self.root_dir=Path(root_dir); self.root_dir.mkdir(parents=True,exist_ok=True)
    def save(self,model):
        if not model.is_fitted: raise RuntimeError("Model belum dilatih dan tidak boleh disimpan.")
        p=self.root_dir/f"{model.metadata.model_id}.json"; p.write_text(json.dumps({"model_type":model.__class__.__name__,"state":model.to_state()},indent=2,sort_keys=True),encoding="utf-8"); return p
    def load(self,model_id):
        p=self.root_dir/f"{model_id}.json"
        if not p.exists(): raise FileNotFoundError(model_id)
        payload=json.loads(p.read_text(encoding="utf-8"))
        if payload.get("model_type")!="MeanThresholdClassifier": raise ValueError("Unsupported model type")
        m=MeanThresholdClassifier(); m.load_state(payload["state"]); m.metadata.model_id=model_id; return m
    def list_models(self): return [{"model_id":p.stem,"path":str(p)} for p in sorted(self.root_dir.glob("MLM-*.json"))]
