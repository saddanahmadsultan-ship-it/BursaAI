"""
BursaAI v6.0 Sprint 6F.2B Dataset Splitter test.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

from Framework.infrastructure import build_infrastructure
from WalkForward.dataset_split_services import (
    register_dataset_splitter,
)
from WalkForward.dataset_splitter import DatasetSplitter
from WalkForward.split_validator import SplitValidator


def build_data():
    dates = pd.bdate_range(
        "2023-01-02",
        "2025-12-31",
    )

    return pd.DataFrame(
        {
            "Open": 10.0,
            "High": 10.5,
            "Low": 9.5,
            "Close": 10.2,
            "Volume": 1000,
        },
        index=dates,
    )


def rolling_windows():
    return [
        {
            "window_id": 1,
            "training_start": "2023-01-02",
            "training_end": "2023-12-29",
            "validation_start": "2024-01-01",
            "validation_end": "2024-03-29",
        },
        {
            "window_id": 2,
            "training_start": "2023-04-03",
            "training_end": "2024-03-29",
            "validation_start": "2024-04-01",
            "validation_end": "2024-06-28",
        },
        {
            "window_id": 3,
            "training_start": "2023-07-03",
            "training_end": "2024-06-28",
            "validation_start": "2024-07-01",
            "validation_end": "2024-09-30",
        },
    ]


def expanding_windows():
    return [
        {
            "window_id": 1,
            "training_start": "2023-01-02",
            "training_end": "2023-12-29",
            "validation_start": "2024-01-01",
            "validation_end": "2024-03-29",
        },
        {
            "window_id": 2,
            "training_start": "2023-01-02",
            "training_end": "2024-03-29",
            "validation_start": "2024-04-01",
            "validation_end": "2024-06-28",
        },
    ]


def main():
    data = build_data()

    splitter = DatasetSplitter(
        minimum_training_rows=200,
        minimum_validation_rows=50,
    )

    rolling = splitter.split_many(
        "1155.KL",
        data,
        rolling_windows(),
    )

    assert len(rolling) == 3
    assert rolling[0].training.rows >= 200
    assert rolling[0].validation.rows >= 50
    assert (
        rolling[0].training.end
        < rolling[0].validation.start
    )

    expanding = splitter.split_many(
        "1155.KL",
        data,
        expanding_windows(),
    )

    assert len(expanding) == 2
    assert (
        expanding[1].training.rows
        > expanding[0].training.rows
    )

    validator = SplitValidator()
    validator.validate(rolling)
    validator.validate(expanding)

    copy_test = rolling[0].training.data
    original_value = data.iloc[0]["Open"]
    copy_test.iloc[0, 0] = 9999

    assert data.iloc[0]["Open"] == original_value

    leakage_detected = False

    try:
        splitter.split_one(
            "1155.KL",
            data,
            {
                "window_id": 99,
                "training_start": "2023-01-02",
                "training_end": "2024-01-31",
                "validation_start": "2024-01-15",
                "validation_end": "2024-03-29",
            },
        )
    except Exception:
        leakage_detected = True

    assert leakage_detected is True

    infrastructure = build_infrastructure()

    registered = register_dataset_splitter(
        infrastructure.services,
        minimum_training_rows=200,
        minimum_validation_rows=50,
    )

    assert (
        infrastructure.services.resolve(
            "dataset_splitter"
        )
        is registered
    )

    print("=" * 90)
    print("BURSAAI v6.0 SPRINT 6F.2B TEST")
    print("=" * 90)
    print("Training Dataset         : OK")
    print("Validation Dataset       : OK")
    print("Rolling Split            : OK")
    print("Expanding Split          : OK")
    print("Multiple Window Split    : OK")
    print("Look-Ahead Prevention    : OK")
    print("Validation Ordering      : OK")
    print("Defensive Data Copy      : OK")
    print("Service Registration     : OK")
    print("=" * 90)
    print("SPRINT 6F.2B DATASET SPLITTER OK")


if __name__ == "__main__":
    main()
