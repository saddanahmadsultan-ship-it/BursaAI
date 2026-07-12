"""
=========================================================
BursaAI Historical Dataset Service Registration
Version : 6.0 Sprint 6F.2A
=========================================================
"""

from __future__ import annotations

from typing import Callable, Optional

import pandas as pd

from Framework.service_container import ServiceContainer
from WalkForward.dataframe_validator import DataFrameValidator
from WalkForward.dataset_builder import HistoricalDatasetBuilder
from WalkForward.dataset_cache import DatasetCache
from WalkForward.history_loader import HistoricalDataLoader


def register_historical_dataset_builder(
    services: ServiceContainer,
    *,
    loader_function: Optional[
        Callable[[str], pd.DataFrame]
    ] = None,
    minimum_rows: int = 50,
    expected_frequency: str = "B",
) -> HistoricalDatasetBuilder:
    loader = HistoricalDataLoader(
        loader=loader_function
    )

    validator = DataFrameValidator(
        minimum_rows=minimum_rows
    )

    cache = DatasetCache()

    builder = HistoricalDatasetBuilder(
        loader=loader,
        validator=validator,
        cache=cache,
        expected_frequency=expected_frequency,
    )

    services.register_instance(
        "historical_data_loader",
        loader,
        replace=True,
    )

    services.register_instance(
        "historical_dataframe_validator",
        validator,
        replace=True,
    )

    services.register_instance(
        "historical_dataset_cache",
        cache,
        replace=True,
    )

    services.register_instance(
        "historical_dataset_builder",
        builder,
        replace=True,
    )

    return builder
