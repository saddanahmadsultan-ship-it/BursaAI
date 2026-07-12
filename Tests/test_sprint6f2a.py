"""
BursaAI v6.0 Sprint 6F.2A Historical Dataset Builder test.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

from Framework.infrastructure import build_infrastructure
from WalkForward.dataframe_validator import DataFrameValidator
from WalkForward.dataset_builder import HistoricalDatasetBuilder
from WalkForward.dataset_cache import DatasetCache
from WalkForward.history_loader import HistoricalDataLoader
from WalkForward.dataset_services import (
    register_historical_dataset_builder,
)


def fake_loader(symbol):
    dates = pd.bdate_range(
        "2025-01-01",
        periods=60,
    )

    data = pd.DataFrame(
        {
            "date": dates,
            "open": [10 + index * 0.01 for index in range(60)],
            "high": [10.2 + index * 0.01 for index in range(60)],
            "low": [9.8 + index * 0.01 for index in range(60)],
            "close": [10.1 + index * 0.01 for index in range(60)],
            "volume": [1000 + index for index in range(60)],
        }
    )

    data = data.sample(
        frac=1.0,
        random_state=7,
    ).reset_index(drop=True)

    return data


def main():
    loader = HistoricalDataLoader(
        loader=fake_loader
    )

    validator = DataFrameValidator(
        minimum_rows=50
    )

    cache = DatasetCache()

    builder = HistoricalDatasetBuilder(
        loader=loader,
        validator=validator,
        cache=cache,
        expected_frequency="B",
    )

    dataset = builder.build(
        "1155.KL"
    )

    assert dataset.symbol == "1155.KL"
    assert len(dataset.data) == 60
    assert isinstance(
        dataset.data.index,
        pd.DatetimeIndex,
    )
    assert dataset.data.index.is_monotonic_increasing
    assert "Open" in dataset.data.columns
    assert "High" in dataset.data.columns
    assert "Low" in dataset.data.columns
    assert "Close" in dataset.data.columns
    assert "Volume" in dataset.data.columns
    assert dataset.metadata["source"] == "loader"
    assert cache.size() == 1

    cached = builder.build(
        "1155.KL"
    )

    assert cached.metadata["source"] == "cache"
    assert cached.data.equals(
        dataset.data
    )

    cached.data.iloc[0, 0] = 9999

    fresh_cache = cache.get(
        "1155.KL:B"
    )

    assert fresh_cache.iloc[0, 0] != 9999

    infrastructure = build_infrastructure()

    registered = register_historical_dataset_builder(
        infrastructure.services,
        loader_function=fake_loader,
        minimum_rows=50,
        expected_frequency="B",
    )

    assert (
        infrastructure.services.resolve(
            "historical_dataset_builder"
        )
        is registered
    )

    registered_dataset = registered.build(
        "1023.KL"
    )

    assert len(
        registered_dataset.data
    ) == 60

    print("=" * 90)
    print("BURSAAI v6.0 SPRINT 6F.2A TEST")
    print("=" * 90)
    print("Historical Data Loader    : OK")
    print("Column Normalization      : OK")
    print("Datetime Normalization    : OK")
    print("OHLCV Validation          : OK")
    print("Numeric Conversion        : OK")
    print("Missing Interval Check    : OK")
    print("Dataset Cache             : OK")
    print("Defensive Cache Copy      : OK")
    print("Service Registration      : OK")
    print("=" * 90)
    print("SPRINT 6F.2A HISTORICAL DATASET BUILDER OK")


if __name__ == "__main__":
    main()
