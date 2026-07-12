"""
=========================================================
BursaAI Dataset Split Service Registration
Version : 6.0 Sprint 6F.2B
=========================================================
"""

from __future__ import annotations

from Framework.service_container import ServiceContainer
from WalkForward.dataset_splitter import DatasetSplitter
from WalkForward.split_validator import SplitValidator


def register_dataset_splitter(
    services: ServiceContainer,
    *,
    minimum_training_rows: int = 50,
    minimum_validation_rows: int = 10,
    copy_data: bool = True,
) -> DatasetSplitter:
    splitter = DatasetSplitter(
        minimum_training_rows=minimum_training_rows,
        minimum_validation_rows=minimum_validation_rows,
        copy_data=copy_data,
    )

    validator = SplitValidator()

    services.register_instance(
        "dataset_splitter",
        splitter,
        replace=True,
    )

    services.register_instance(
        "dataset_split_validator",
        validator,
        replace=True,
    )

    return splitter
