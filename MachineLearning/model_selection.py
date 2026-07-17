from dataclasses import dataclass
@dataclass
class ModelSelectionConfig:
    validation_weight: float=.35; test_weight: float=.25; f1_weight: float=.20; stability_weight: float=.15; gap_penalty_weight: float=.05
class ModelSelector:
    def __init__(self,config=None): self.config=config or ModelSelectionConfig()
    def calculate_score(self,r):
        c=self.config; s=r.validation_metrics.balanced_accuracy*c.validation_weight+r.test_metrics.balanced_accuracy*c.test_weight+r.test_metrics.f1_score*c.f1_weight+r.stability_score*c.stability_weight-r.generalization_gap*c.gap_penalty_weight
        return round(max(0,min(1,s)),6)
    def rank(self,results):
        items=list(results)
        for r in items: r.selection_score=self.calculate_score(r)
        return sorted(items,key=lambda r:(r.selection_score,r.test_metrics.f1_score,r.stability_score),reverse=True)
