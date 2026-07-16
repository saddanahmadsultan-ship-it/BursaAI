from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Dict, List

from MachineLearning.dataset import MLDataset


@dataclass
class DatasetValidationReport:
    passed: bool
    sample_count: int
    feature_count: int
    positive_count: int
    negative_count: int
    duplicate_count: int
    issues: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)


class ResearchDatasetValidator:
    def validate(
        self,
        dataset: MLDataset,
    ) -> DatasetValidationReport:
        issues: List[str] = []

        if dataset.size == 0:
            issues.append("Dataset kosong.")

        if not dataset.feature_names:
            issues.append("Dataset tiada feature.")

        duplicate_count = self._duplicate_count(dataset)

        if duplicate_count:
            issues.append(
                f"Duplicate rows detected: {duplicate_count}"
            )

        invalid_values = 0

        for row in dataset.rows:
            for value in row.values():
                if not math.isfinite(float(value)):
                    invalid_values += 1

        if invalid_values:
            issues.append(
                f"NaN/Inf values detected: {invalid_values}"
            )

        positive_count = sum(
            target >= 0.5
            for target in dataset.targets
        )

        negative_count = dataset.size - positive_count

        if dataset.size > 1 and (
            positive_count == 0
            or negative_count == 0
        ):
            issues.append(
                "Target hanya mempunyai satu kelas."
            )

        return DatasetValidationReport(
            passed=not issues,
            sample_count=dataset.size,
            feature_count=len(dataset.feature_names),
            positive_count=positive_count,
            negative_count=negative_count,
            duplicate_count=duplicate_count,
            issues=issues,
        )

    @staticmethod
    def _duplicate_count(
        dataset: MLDataset,
    ) -> int:
        seen = set()
        duplicates = 0

        for row, target in zip(
            dataset.rows,
            dataset.targets,
        ):
            key = (
                tuple(
                    (name, row[name])
                    for name in dataset.feature_names
                ),
                float(target),
            )

            if key in seen:
                duplicates += 1
            else:
                seen.add(key)

        return duplicates
