from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ConsistencyWeights:
    fold_consistency: float = 0.25
    monthly_stability: float = 0.20
    yearly_stability: float = 0.15
    equity_smoothness: float = 0.20
    return_reliability: float = 0.20

    def __post_init__(self) -> None:
        values = [
            self.fold_consistency,
            self.monthly_stability,
            self.yearly_stability,
            self.equity_smoothness,
            self.return_reliability,
        ]

        if any(value < 0 for value in values):
            raise ValueError("Consistency weight tidak boleh negatif.")

        total = sum(values)

        if total <= 0:
            raise ValueError("Jumlah consistency weight mesti lebih besar daripada 0.")

        self.fold_consistency /= total
        self.monthly_stability /= total
        self.yearly_stability /= total
        self.equity_smoothness /= total
        self.return_reliability /= total
