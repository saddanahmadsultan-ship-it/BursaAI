"""
BursaAI v6.0 Sprint 6F.4 Validation Window Runner test.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

from Framework.infrastructure import build_infrastructure
from WalkForward.dataset_splitter import DatasetSplitter
from WalkForward.training_models import TrainingWindowResult
from WalkForward.validation_report import ValidationReport
from WalkForward.validation_services import (
    register_validation_runner,
)


def build_data():
    dates = pd.bdate_range(
        "2022-01-03",
        "2024-12-31",
    )

    closes = [
        10 + index * 0.01
        for index in range(len(dates))
    ]

    return pd.DataFrame(
        {
            "Open": closes,
            "High": [
                value + 0.2
                for value in closes
            ],
            "Low": [
                value - 0.2
                for value in closes
            ],
            "Close": closes,
            "Volume": [
                1000 + index
                for index in range(len(dates))
            ],
        },
        index=dates,
    )


def build_splits():
    windows = [
        {
            "window_id": 1,
            "training_start": "2022-01-03",
            "training_end": "2022-12-30",
            "validation_start": "2023-01-02",
            "validation_end": "2023-03-31",
        },
        {
            "window_id": 2,
            "training_start": "2022-04-01",
            "training_end": "2023-03-31",
            "validation_start": "2023-04-03",
            "validation_end": "2023-06-30",
        },
        {
            "window_id": 3,
            "training_start": "2022-07-01",
            "training_end": "2023-06-30",
            "validation_start": "2023-07-03",
            "validation_end": "2023-09-29",
        },
    ]

    splitter = DatasetSplitter(
        minimum_training_rows=200,
        minimum_validation_rows=50,
    )

    return splitter.split_many(
        "1155.KL",
        build_data(),
        windows,
    )


def build_training_results():
    return [
        TrainingWindowResult(
            window_id=1,
            symbol="1155.KL",
            success=True,
            parameters={
                "short_window": 21,
                "long_window": 51,
            },
            metrics={
                "training_score": 71,
            },
        ),
        TrainingWindowResult(
            window_id=2,
            symbol="1155.KL",
            success=True,
            parameters={
                "short_window": 22,
                "long_window": 52,
            },
            metrics={
                "training_score": 72,
            },
        ),
        TrainingWindowResult(
            window_id=3,
            symbol="1155.KL",
            success=True,
            parameters={
                "short_window": 23,
                "long_window": 53,
            },
            metrics={
                "training_score": 73,
            },
        ),
    ]


def fake_validator(data, parameters, split, context):
    first_close = float(data["Close"].iloc[0])
    last_close = float(data["Close"].iloc[-1])
    validation_return = (
        (last_close - first_close)
        / first_close
        * 100
    )

    return {
        "metrics": {
            "validation_return": validation_return,
            "validation_score": (
                80 + split.window_id
            ),
            "rows": len(data),
        },
        "predictions": [
            {
                "date": data.index[-1].isoformat(),
                "signal": "BUY",
            }
        ],
        "artifacts": {
            "used_short_window": parameters["short_window"],
            "used_long_window": parameters["long_window"],
        },
        "warnings": [],
    }


def main():
    infrastructure = build_infrastructure()
    events = []

    infrastructure.events.subscribe(
        "ValidationWindowCompleted",
        lambda event: events.append(event.name),
    )

    infrastructure.events.subscribe(
        "ValidationRunCompleted",
        lambda event: events.append(event.name),
    )

    runner = register_validation_runner(
        infrastructure.services,
        validator=fake_validator,
        validator_name="moving_average",
    )

    result = runner.run_many(
        build_splits(),
        build_training_results(),
        context={
            "strategy": "moving_average",
        },
    )

    assert result.total_windows == 3
    assert result.successful_windows == 3
    assert result.failed_windows == 0
    assert result.success is True
    assert len(result.results) == 3

    first = result.results[0]

    assert first.success is True
    assert first.parameters["short_window"] == 21
    assert first.metrics["validation_score"] == 81.0
    assert first.metrics["rows"] >= 50
    assert len(first.predictions) == 1
    assert first.artifacts["used_long_window"] == 51

    assert events.count(
        "ValidationWindowCompleted"
    ) == 3

    assert events.count(
        "ValidationRunCompleted"
    ) == 1

    registry = infrastructure.services.resolve(
        "validation_registry"
    )

    assert registry.names() == [
        "moving_average"
    ]

    assert (
        infrastructure.services.resolve(
            "validation_window_runner"
        )
        is runner
    )

    report = ValidationReport(
        result=result
    )

    rendered = report.render_text()

    assert "BURSAAI VALIDATION WINDOW REPORT" in rendered
    assert "Total Windows       : 3" in rendered
    assert "Successful Windows  : 3" in rendered

    print("=" * 90)
    print("BURSAAI v6.0 SPRINT 6F.4 TEST")
    print("=" * 90)
    print("Validation Window Model  : OK")
    print("Validation Run Model     : OK")
    print("Validation Registry      : OK")
    print("Single Window Validation : OK")
    print("Multiple Window Runner   : OK")
    print("Training Parameter Link  : OK")
    print("Metric Capture           : OK")
    print("Prediction Capture       : OK")
    print("Artifact Capture         : OK")
    print("Validation Events        : OK")
    print("Service Registration     : OK")
    print("Validation Report        : OK")
    print("=" * 90)
    print("SPRINT 6F.4 VALIDATION WINDOW RUNNER OK")


if __name__ == "__main__":
    main()
