from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RobustnessWeights:
    fold_success: float = 0.25
    degradation: float = 0.25
    fold_dispersion: float = 0.20
    parameter_stability: float = 0.15
    regime_stability: float = 0.15

    def __post_init__(self) -> None:
        values = [
            self.fold_success,
            self.degradation,
            self.fold_dispersion,
            self.parameter_stability,
            self.regime_stability,
        ]

        if any(value < 0 for value in values):
            raise ValueError("Robustness weight tidak boleh negatif.")

        total = sum(values)

        if total <= 0:
            raise ValueError("Jumlah robustness weight mesti lebih besar daripada 0.")

        self.fold_success /= total
        self.degradation /= total
        self.fold_dispersion /= total
        self.parameter_stability /= total
        self.regime_stability /= total
