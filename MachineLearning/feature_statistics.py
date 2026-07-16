from __future__ import annotations

from dataclasses import asdict, dataclass
from statistics import mean, median, pvariance
from typing import Dict, Iterable, List

from MachineLearning.dataset import MLDataset


@dataclass
class FeatureStatistic:
    count: int
    minimum: float
    maximum: float
    mean: float
    median: float
    variance: float

    def to_dict(self) -> Dict:
        return asdict(self)


class FeatureStatistics:
    def calculate(
        self,
        dataset: MLDataset,
    ) -> Dict[str, FeatureStatistic]:
        result: Dict[str, FeatureStatistic] = {}

        for name in dataset.feature_names:
            values = [
                float(row[name])
                for row in dataset.rows
            ]

            if not values:
                continue

            result[name] = FeatureStatistic(
                count=len(values),
                minimum=min(values),
                maximum=max(values),
                mean=mean(values),
                median=median(values),
                variance=pvariance(values)
                if len(values) > 1
                else 0.0,
            )

        return result

    def target_balance(
        self,
        dataset: MLDataset,
    ) -> Dict[str, float]:
        if dataset.size == 0:
            return {
                "positive_ratio": 0.0,
                "negative_ratio": 0.0,
            }

        positive = sum(
            value >= 0.5
            for value in dataset.targets
        )

        return {
            "positive_ratio": positive / dataset.size,
            "negative_ratio": (
                dataset.size - positive
            ) / dataset.size,
        }
