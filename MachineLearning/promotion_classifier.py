from __future__ import annotations
from dataclasses import dataclass

@dataclass
class PromotionThresholds:
    promote_to_paper: float = 0.88
    promote_to_stress: float = 0.72
    review: float = 0.52
    minimum_confidence: float = 0.18

class MLPromotionClassifier:
    def __init__(self, thresholds=None): self.thresholds=thresholds or PromotionThresholds()
    def classify(self, probability: float, confidence: float):
        p=float(probability); c=float(confidence)
        if c < self.thresholds.minimum_confidence:
            return "HOLD_FOR_MORE_DATA", "Prediction confidence below deployment threshold."
        if p >= self.thresholds.promote_to_paper:
            return "PROMOTE_TO_PAPER_TRADING", "ML probability passed paper-trading gate."
        if p >= self.thresholds.promote_to_stress:
            return "ADVANCE_TO_STRESS_TEST", "ML probability passed stress-test gate."
        if p >= self.thresholds.review:
            return "REVIEW_AND_RETUNE", "Candidate is borderline and requires retuning."
        return "REJECT_FROM_PROMOTION", "ML probability failed promotion gate."
