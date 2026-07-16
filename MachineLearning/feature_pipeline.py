from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from MachineLearning.dataset_export import (
    DatasetExporter,
)
from MachineLearning.dataset_validator import (
    ResearchDatasetValidator,
)
from MachineLearning.research_dataset_builder import (
    ResearchDatasetBuilder,
)


@dataclass
class FeaturePipelineConfig:
    output_dir: Path
    scale_features: bool = False
    fail_on_validation_error: bool = True


class ResearchFeaturePipeline:
    def __init__(
        self,
        config: FeaturePipelineConfig,
        builder: ResearchDatasetBuilder | None = None,
        validator: ResearchDatasetValidator | None = None,
    ) -> None:
        self.config = config
        self.builder = (
            builder
            or ResearchDatasetBuilder()
        )
        self.validator = (
            validator
            or ResearchDatasetValidator()
        )

    def run(
        self,
        ranked_strategies: Iterable[Any],
        pareto_points: Iterable[Any] | None = None,
        promotions: Iterable[Mapping[str, Any]] | None = None,
    ) -> Dict[str, Any]:
        dataset = self.builder.build(
            ranked_strategies=ranked_strategies,
            pareto_points=pareto_points,
            promotions=promotions,
            scale=self.config.scale_features,
        )

        validation = self.validator.validate(
            dataset
        )

        if (
            self.config.fail_on_validation_error
            and not validation.passed
        ):
            raise ValueError(
                "Dataset validation failed: "
                + "; ".join(validation.issues)
            )

        outputs = DatasetExporter(
            self.config.output_dir
        ).export_all(
            dataset,
            validation,
        )

        return {
            "dataset": dataset,
            "validation": validation,
            "outputs": outputs,
        }
