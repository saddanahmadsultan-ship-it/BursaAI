from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict

from MachineLearning.dataset import MLDataset
from MachineLearning.feature_statistics import FeatureStatistics
from MachineLearning.dataset_validator import DatasetValidationReport


class DatasetExporter:
    def __init__(
        self,
        output_dir: str | Path = "Datasets",
    ) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def export_all(
        self,
        dataset: MLDataset,
        validation: DatasetValidationReport,
    ) -> Dict[str, Path]:
        return {
            "csv": self.export_csv(dataset),
            "json": self.export_json(dataset),
            "summary": self.export_summary(
                dataset,
                validation,
            ),
        }

    def export_csv(
        self,
        dataset: MLDataset,
    ) -> Path:
        path = self.output_dir / "research_ml_dataset.csv"
        fieldnames = (
            dataset.feature_names
            + [dataset.schema.target_name]
        )

        with open(
            path,
            "w",
            newline="",
            encoding="utf-8-sig",
        ) as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=fieldnames,
            )
            writer.writeheader()

            for row, target in zip(
                dataset.rows,
                dataset.targets,
            ):
                payload = dict(row)
                payload[dataset.schema.target_name] = target
                writer.writerow(payload)

        return path

    def export_json(
        self,
        dataset: MLDataset,
    ) -> Path:
        path = self.output_dir / "research_ml_dataset.json"

        payload = {
            "schema": dataset.schema.to_dict(),
            "rows": [
                {
                    **row,
                    dataset.schema.target_name: target,
                    "metadata": metadata,
                }
                for row, target, metadata in zip(
                    dataset.rows,
                    dataset.targets,
                    dataset.metadata,
                )
            ],
        }

        path.write_text(
            json.dumps(
                payload,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

        return path

    def export_summary(
        self,
        dataset: MLDataset,
        validation: DatasetValidationReport,
    ) -> Path:
        path = self.output_dir / "research_ml_summary.json"
        statistics = FeatureStatistics()

        payload = {
            "validation": validation.to_dict(),
            "target_balance": statistics.target_balance(
                dataset
            ),
            "feature_statistics": {
                name: item.to_dict()
                for name, item in statistics.calculate(
                    dataset
                ).items()
            },
        }

        path.write_text(
            json.dumps(
                payload,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

        return path
