from pathlib import Path
import json, joblib
class SklearnModelRegistry:
    def __init__(self,root_dir='Models'): self.root_dir=Path(root_dir); self.root_dir.mkdir(parents=True,exist_ok=True)
    def save(self,model):
        if not model.is_fitted: raise RuntimeError('Model belum dilatih.')
        p=self.root_dir/f'{model.metadata.model_id}.joblib'; joblib.dump(model.estimator,p); (self.root_dir/f'{model.metadata.model_id}.json').write_text(json.dumps(model.metadata.to_dict(),indent=2),encoding='utf-8'); return p
