from pathlib import Path
import json,csv
class ModelEvaluationReport:
    def __init__(self,output_dir='Reports/ML'): self.output_dir=Path(output_dir); self.output_dir.mkdir(parents=True,exist_ok=True)
    def export(self,results):
        items=list(results); jp=self.output_dir/'model_evaluation.json'; cp=self.output_dir/'model_evaluation.csv'; sp=self.output_dir/'model_selection_summary.json'; jp.write_text(json.dumps([x.to_dict() for x in items],indent=2),encoding='utf-8')
        fields=['rank','model_name','selection_score','validation_balanced_accuracy','test_balanced_accuracy','test_f1','generalization_gap','cross_validation_mean','cross_validation_std','stability_score','model_path']
        with cp.open('w',newline='',encoding='utf-8-sig') as h:
            w=csv.DictWriter(h,fieldnames=fields); w.writeheader()
            for i,x in enumerate(items,1): w.writerow({'rank':i,'model_name':x.model_name,'selection_score':x.selection_score,'validation_balanced_accuracy':x.validation_metrics.balanced_accuracy,'test_balanced_accuracy':x.test_metrics.balanced_accuracy,'test_f1':x.test_metrics.f1_score,'generalization_gap':x.generalization_gap,'cross_validation_mean':x.cross_validation_mean,'cross_validation_std':x.cross_validation_std,'stability_score':x.stability_score,'model_path':x.model_path})
        sp.write_text(json.dumps({'total_models':len(items),'best_model':items[0].to_dict() if items else None},indent=2),encoding='utf-8'); return {'json':jp,'csv':cp,'summary':sp}
