"""
BursaAI v6.0 Sprint 6F.8 Full Walk Forward Pipeline test.
"""

from pathlib import Path
import sys
import tempfile

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

from Framework.infrastructure import build_infrastructure
from WalkForward.analyzer_services import (
    register_walkforward_analyzer,
)
from WalkForward.dataset_services import (
    register_historical_dataset_builder,
)
from WalkForward.dataset_split_services import (
    register_dataset_splitter,
)
from WalkForward.final_report_services import (
    register_walkforward_final_report,
)
from WalkForward.historical_services import (
    register_historical_engine,
)
from WalkForward.optimization_services import (
    register_optimization_engine,
)
from WalkForward.optimization_workflow_services import (
    register_optimization_workflow,
)
from WalkForward.parameter_services import (
    register_parameter_generator,
)
from WalkForward.parameter_space import ParameterSpace
from WalkForward.pipeline_report import (
    WalkForwardPipelineReport,
)
from WalkForward.pipeline_services import (
    register_walkforward_pipeline,
)
from WalkForward.training_services import (
    register_training_runner,
)
from WalkForward.validation_services import (
    register_validation_runner,
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
            "Volume": [1000 + index for index in range(len(dates))],
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
        "artifacts": {
            "model": f"window_{split.window_id}",
        },
    }


def fake_validator(data, parameters, split, context=None):
    return {
        "metrics": {
            "validation_score": 78 + split.window_id,
        },
        "predictions": [
            {
                "signal": "BUY",
            }
        ],
        "artifacts": {
            "parameters": dict(parameters),
        },
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
        },
        "artifacts": {
            "name": f"EMA_{fast}_{slow}",
        },
    }


def build_parameter_space():
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


def main():
    infrastructure = build_infrastructure()
    events = []

    infrastructure.events.subscribe(
        "WalkForwardPipelineStarted",
        lambda event: events.append(event.name),
    )

    infrastructure.events.subscribe(
        "WalkForwardPipelineCompleted",
        lambda event: events.append(event.name),
    )

    register_historical_dataset_builder(
        infrastructure.services,
        loader_function=fake_loader,
        minimum_rows=200,
        expected_frequency="B",
    )

    register_dataset_splitter(
        infrastructure.services,
        minimum_training_rows=200,
        minimum_validation_rows=50,
    )

    infrastructure.services.register_instance(
        "walkforward_window_generator",
        FakeWindowGenerator(),
        replace=True,
    )

    register_historical_engine(
        infrastructure.services
    )

    register_training_runner(
        infrastructure.services,
        trainer=fake_trainer,
        trainer_name="ema",
    )

    register_validation_runner(
        infrastructure.services,
        validator=fake_validator,
        validator_name="ema",
    )

    register_walkforward_analyzer(
        infrastructure.services,
        maximum_degradation_percent=20,
        minimum_validation_metric=60,
        minimum_pass_rate_percent=60,
    )

    register_parameter_generator(
        infrastructure.services,
        parameter_space=build_parameter_space(),
        random_seed=42,
    )

    register_optimization_engine(
        infrastructure.services,
        evaluator=fake_optimizer,
        optimizer_name="grid",
    )

    register_optimization_workflow(
        infrastructure.services
    )

    register_walkforward_final_report(
        infrastructure.services
    )

    pipeline = register_walkforward_pipeline(
        infrastructure.services,
        pipeline_name="ema_pipeline",
        stop_on_error=True,
    )

    with tempfile.TemporaryDirectory() as folder:
        result = pipeline.run(
            "1155.KL",
            strategy_name="ema_cross",
            training_metric_name="training_score",
            validation_metric_name="validation_score",
            optimization_mode="grid",
            export_report=True,
            output_directory=folder,
            metadata={
                "test_run": True,
            },
        )

        assert result.success is True
        assert result.completed_stages == 7
        assert result.failed_stages == 0
        assert result.historical_result.windows_generated == 3
        assert result.training_result.successful_windows == 3
        assert result.validation_result.successful_windows == 3
        assert result.analysis_result.verdict == "ROBUST"
        assert result.optimization_result.best_candidate is not None
        assert result.final_report.summary.recommendation == (
            "APPROVED FOR PAPER TRADING"
        )
        assert Path(result.export_paths["text"]).exists()
        assert Path(result.export_paths["json"]).exists()

        report = WalkForwardPipelineReport(
            result=result
        )

        rendered = report.render_text()

        assert "BURSAAI WALK FORWARD PIPELINE" in rendered
        assert "Status                 : SUCCESS" in rendered
        assert "Completed Stages       : 7" in rendered

    registry = infrastructure.services.resolve(
        "walkforward_pipeline_registry"
    )

    assert registry.names() == [
        "ema_pipeline"
    ]

    assert (
        registry.get("ema_pipeline")
        is pipeline
    )

    assert (
        infrastructure.services.resolve(
            "walkforward_pipeline"
        )
        is pipeline
    )

    assert "WalkForwardPipelineStarted" in events
    assert "WalkForwardPipelineCompleted" in events

    print("=" * 98)
    print("BURSAAI v6.0 SPRINT 6F.8 TEST")
    print("=" * 98)
    print("Pipeline Context                 : OK")
    print("Pipeline Models                  : OK")
    print("Historical Integration           : OK")
    print("Training Integration             : OK")
    print("Validation Integration           : OK")
    print("Analyzer Integration             : OK")
    print("Optimization Integration         : OK")
    print("Final Report Integration         : OK")
    print("Report Export                    : OK")
    print("Pipeline Registry                : OK")
    print("Pipeline Events                  : OK")
    print("Service Registration             : OK")
    print("Full End-to-End Walk Forward     : OK")
    print("=" * 98)
    print("SPRINT 6F.8 FULL WALK FORWARD PIPELINE OK")


if __name__ == "__main__":
    main()
