"""
BursaAI v6 Sprint 6G.2 Walk Forward Bootstrap + Release Health Test.
"""

from pathlib import Path
import sys
import tempfile

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

from Bootstrap.release_health_report import (
    ReleaseHealthReport,
)
from Bootstrap.walkforward_bootstrap import (
    WalkForwardBootstrap,
    WalkForwardBootstrapOptions,
)
from Framework.infrastructure import (
    build_infrastructure,
)
from WalkForward.parameter_space import (
    ParameterSpace,
)


def fake_loader(symbol):
    dates = pd.bdate_range(
        "2022-01-03",
        "2025-12-31",
    )

    values = [
        10 + index * 0.01
        for index in range(len(dates))
    ]

    return pd.DataFrame(
        {
            "Open": values,
            "High": [value + 0.2 for value in values],
            "Low": [value - 0.2 for value in values],
            "Close": [value + 0.1 for value in values],
            "Volume": [
                1000 + index
                for index in range(len(dates))
            ],
        },
        index=dates,
    )


class FakeWindowGenerator:
    def generate(self, data, symbol=None, config=None):
        return [
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


def fake_trainer(data, split, context=None):
    return {
        "parameters": {
            "ema_fast": 10,
            "ema_slow": 50,
        },
        "metrics": {
            "training_score": 82 + split.window_id,
        },
    }


def fake_validator(data, parameters, split, context=None):
    return {
        "metrics": {
            "validation_score": 78 + split.window_id,
        },
        "predictions": [],
    }


def fake_optimizer(parameters, context=None):
    if hasattr(parameters, "parameters"):
        parameters = parameters.parameters

    fast = parameters["ema_fast"]
    slow = parameters["ema_slow"]

    return {
        "metrics": {
            "robustness_score": 95 - abs(fast - 10) * 2,
            "profit_factor": 2.2 - abs(slow - 50) * 0.01,
            "sharpe_ratio": 1.8,
            "drawdown_score": 90,
            "win_rate": 63,
            "stability_score": 92,
        }
    }


def build_space():
    space = ParameterSpace()

    space.add(
        "ema_fast",
        [5, 10, 15],
    )

    space.add(
        "ema_slow",
        [30, 50, 70],
    )

    space.add_constraint(
        lambda parameters: (
            parameters["ema_fast"]
            < parameters["ema_slow"]
        )
    )

    return space


class ApplicationStub:
    def __init__(self, infrastructure):
        self.infrastructure = infrastructure
        self.services = infrastructure.services


def main():
    infrastructure = build_infrastructure()

    options = WalkForwardBootstrapOptions(
        minimum_rows=200,
        minimum_training_rows=200,
        minimum_validation_rows=50,
        pipeline_name="release_test",
        stop_on_error=True,
    )

    pipeline = WalkForwardBootstrap(
        options
    ).register(
        infrastructure.services,
        loader_function=fake_loader,
        window_generator=FakeWindowGenerator(),
        trainer=fake_trainer,
        validator=fake_validator,
        parameter_space=build_space(),
        optimization_evaluator=fake_optimizer,
    )

    assert pipeline is not None

    required = (
        WalkForwardBootstrap.REQUIRED_SERVICES
    )

    for name in required:
        assert infrastructure.services.contains(
            name
        )

    with tempfile.TemporaryDirectory() as folder:
        result = pipeline.run(
            "1155.KL",
            strategy_name="ema_cross",
            export_report=True,
            output_directory=folder,
        )

        assert result.success is True
        assert result.completed_stages == 7
        assert result.failed_stages == 0
        assert result.analysis_result.verdict == "ROBUST"
        assert (
            result.final_report.summary.recommendation
            == "APPROVED FOR PAPER TRADING"
        )

        from Bootstrap.release_health import (
            ReleaseHealthChecker,
        )

        checker = ReleaseHealthChecker(
            ApplicationStub(infrastructure)
        )

        health = checker.run(
            required_services=required,
            walkforward_dry_run=True,
            symbol="1155.KL",
            strategy_name="ema_cross",
            output_directory=folder,
        )

        assert health.success is True
        assert health.failed == 0
        assert health.passed == len(required) + 1

        report = ReleaseHealthReport(
            result=health
        )

        rendered = report.render_text()

        assert (
            "BURSAAI v6 RELEASE HEALTH CHECK"
            in rendered
        )
        assert "Status : HEALTHY" in rendered

    print("=" * 96)
    print("BURSAAI v6.0 SPRINT 6G.2 TEST")
    print("=" * 96)
    print("Historical Service Bootstrap  : OK")
    print("Training Service Bootstrap    : OK")
    print("Validation Service Bootstrap  : OK")
    print("Analyzer Service Bootstrap    : OK")
    print("Optimization Bootstrap        : OK")
    print("Final Report Bootstrap        : OK")
    print("Pipeline Bootstrap            : OK")
    print("Required Service Validation   : OK")
    print("Walk Forward Dry Run          : OK")
    print("Release Health Check          : OK")
    print("Health Report                 : OK")
    print("=" * 96)
    print("SPRINT 6G.2 WALK FORWARD BOOTSTRAP & RELEASE HEALTH OK")


if __name__ == "__main__":
    main()
