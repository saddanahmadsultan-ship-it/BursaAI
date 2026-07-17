from __future__ import annotations
import math

class ConfidenceCalibrator:
    def __init__(self, temperature: float = 1.25):
        if temperature <= 0: raise ValueError("temperature mesti positif")
        self.temperature=float(temperature)
    def calibrate(self, probability: float) -> float:
        p=min(max(float(probability),1e-6),1-1e-6)
        logit=math.log(p/(1-p))/self.temperature
        return round(1/(1+math.exp(-logit)),6)
    @staticmethod
    def confidence(probability: float) -> float:
        return round(abs(float(probability)-0.5)*2.0,6)
