from dataclasses import dataclass, asdict
from typing import Any, Dict
@dataclass
class ClassificationMetrics:
    accuracy: float; precision: float; recall: float; f1_score: float; specificity: float; balanced_accuracy: float
    true_positive: int; true_negative: int; false_positive: int; false_negative: int
    def to_dict(self)->Dict[str,Any]: return asdict(self)
@dataclass
class ModelEvaluationResult:
    model_name: str; model_type: str; train_metrics: ClassificationMetrics; validation_metrics: ClassificationMetrics; test_metrics: ClassificationMetrics
    generalization_gap: float; cross_validation_mean: float; cross_validation_std: float; stability_score: float; selection_score: float; model_path: str=''
    def to_dict(self)->Dict[str,Any]: return asdict(self)
