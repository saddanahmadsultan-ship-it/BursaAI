from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean, pstdev
from typing import Dict, Iterable, List


@dataclass
class StandardFeatureScaler:
    means: Dict[str, float] = field(default_factory=dict)
    scales: Dict[str, float] = field(default_factory=dict)
    fitted: bool = False

    def fit(
        self,
        rows: Iterable[Dict[str, float]],
    ) -> None:
        items = list(rows)

        if not items:
            raise ValueError("Scaler memerlukan sekurang-kurangnya satu row.")

        feature_names = list(items[0].keys())

        self.means = {}
        self.scales = {}

        for name in feature_names:
            values = [
                float(row[name])
                for row in items
            ]

            center = mean(values)
            scale = pstdev(values) if len(values) > 1 else 0.0

            self.means[name] = center
            self.scales[name] = scale if scale > 1e-12 else 1.0

        self.fitted = True

    def transform_row(
        self,
        row: Dict[str, float],
    ) -> Dict[str, float]:
        if not self.fitted:
            raise RuntimeError("Scaler belum fitted.")

        return {
            name: round(
                (
                    float(row.get(name, self.means[name]))
                    - self.means[name]
                )
                / self.scales[name],
                8,
            )
            for name in self.means
        }

    def transform(
        self,
        rows: Iterable[Dict[str, float]],
    ) -> List[Dict[str, float]]:
        return [
            self.transform_row(row)
            for row in rows
        ]
