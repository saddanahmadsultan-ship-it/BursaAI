from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

class ActiveModelRegistry:
    def __init__(self, root_dir='Models/Sprint7B4'):
        self.root=Path(root_dir); self.root.mkdir(parents=True,exist_ok=True); self.manifest=self.root/'active_models.json'
    def promote_champion(self, model_path, model_name='', selection_score=0.0, feature_names=None):
        p=Path(model_path)
        payload={'champion':{'model_id':p.stem,'model_path':str(p),'metadata_path':str(p.with_suffix('.json')),'model_name':model_name,'selection_score':float(selection_score),'feature_names':list(feature_names or []),'activated_at':datetime.now(timezone.utc).isoformat()},'challengers':[]}
        if self.manifest.exists():
            old=json.loads(self.manifest.read_text(encoding='utf-8')); previous=old.get('champion')
            if previous and previous.get('model_id') != p.stem: payload['challengers']=[previous]+old.get('challengers',[])
        self.manifest.write_text(json.dumps(payload,indent=2,sort_keys=True),encoding='utf-8'); return payload['champion']
    def load_manifest(self):
        if not self.manifest.exists(): raise FileNotFoundError(f'Active model manifest not found: {self.manifest}')
        return json.loads(self.manifest.read_text(encoding='utf-8'))
    def active_entries(self, include_challengers=False):
        m=self.load_manifest(); out=[m['champion']]
        if include_challengers: out.extend(m.get('challengers',[]))
        return out
