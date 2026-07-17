from __future__ import annotations
import csv,json
from pathlib import Path

class PredictionReport:
    def __init__(self, output_dir='Reports/ML/Predictions'): self.output=Path(output_dir); self.output.mkdir(parents=True,exist_ok=True)
    def export(self, predictions):
        rows=[p.to_dict() if hasattr(p,'to_dict') else dict(p) for p in predictions]; jp=self.output/'promotion_predictions.json'; cp=self.output/'promotion_predictions.csv'; jp.write_text(json.dumps(rows,indent=2,ensure_ascii=False,sort_keys=True),encoding='utf-8')
        fields=['candidate_id','probability','calibrated_probability','confidence','predicted_class','decision','reason','model_version','cache_hit','created_at']
        with cp.open('w',newline='',encoding='utf-8-sig') as h:
            w=csv.DictWriter(h,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(rows)
        return {'json':jp,'csv':cp}
