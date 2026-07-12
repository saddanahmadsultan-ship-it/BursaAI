from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RankingWeights:
    performance: float = 0.35
    risk: float = 0.20
    consistency: float = 0.20
    robustness: float = 0.20
    confidence: float = 0.05

    def __post_init__(self) -> None:
        values = [
            self.performance,
            self.risk,
            self.consistency,
            self.robustness,
            self.confidence,
        ]

        if any(value < 0 for value in values):
            raise ValueError("Ranking weight tidak boleh negatif.")

        total = sum(values)

        if total <= 0:
            raise ValueError("Jumlah ranking weight mesti lebih besar daripada 0.")

        self.performance /= total
        self.risk /= total
        self.consistency /= total
        self.robustness /= total
        self.confidence /= total
