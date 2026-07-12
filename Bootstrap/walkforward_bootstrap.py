"""
=========================================================
BursaAI Walk Forward Bootstrap
Version : 6.0 Sprint 6G.2
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

from Framework.service_container import ServiceContainer
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
from WalkForward.pipeline_services import (
    register_walkforward_pipeline,
)
from WalkForward.training_services import (
    register_training_runner,
)
from WalkForward.validation_services import (
    register_validation_runner,
)


@dataclass(slots=True)
class WalkForwardBootstrapOptions:
    minimum_rows: int = 200
    minimum_training_rows: int = 150
    minimum_validation_rows: int = 30
    expected_frequency: str = "B"

    maximum_degradation_percent: float = 30.0
    minimum_validation_metric: float = 0.0
    minimum_pass_rate_percent: float = 60.0

    optimizer_name: str = "grid"
    pipeline_name: str = "default"
    random_seed: int = 42
    stop_on_error: bool = True


class WalkForwardBootstrap:
    REQUIRED_SERVICES = [
        "historical_dataset_builder",
        "dataset_splitter",
        "dataset_split_validator",
        "historical_engine",
        "training_registry",
        "training_window_runner",
        "validation_registry",
        "validation_window_runner",
        "walkforward_analyzer",
        "optimization_parameter_space",
        "optimization_parameter_generator",
        "optimization_registry",
        "optimization_engine",
        "optimization_workflow",
        "walkforward_final_report_builder",
        "walkforward_final_report_exporter",
        "walkforward_pipeline_registry",
        "walkforward_pipeline",
    ]

    def __init__(
        self,
        options: Optional[WalkForwardBootstrapOptions] = None,
    ):
        self.options = (
            options
            or WalkForwardBootstrapOptions()
        )

    def register(
        self,
        services: ServiceContainer,
        *,
        loader_function: Callable,
        window_generator: Any,
        trainer: Callable,
        validator: Callable,
        parameter_space: ParameterSpace,
        optimization_evaluator: Callable,
    ):
        register_historical_dataset_builder(
            services,
            loader_function=loader_function,
            minimum_rows=self.options.minimum_rows,
            expected_frequency=self.options.expected_frequency,
        )

        register_dataset_splitter(
            services,
            minimum_training_rows=(
                self.options.minimum_training_rows
            ),
            minimum_validation_rows=(
                self.options.minimum_validation_rows
            ),
        )

        services.register_instance(
            "walkforward_window_generator",
            window_generator,
            replace=True,
        )

        register_historical_engine(
            services
        )

        register_training_runner(
            services,
            trainer=trainer,
            trainer_name="default",
            stop_on_error=self.options.stop_on_error,
        )

        register_validation_runner(
            services,
            validator=validator,
            validator_name="default",
            stop_on_error=self.options.stop_on_error,
        )

        register_walkforward_analyzer(
            services,
            maximum_degradation_percent=(
                self.options.maximum_degradation_percent
            ),
            minimum_validation_metric=(
                self.options.minimum_validation_metric
            ),
            minimum_pass_rate_percent=(
                self.options.minimum_pass_rate_percent
            ),
        )

        register_parameter_generator(
            services,
            parameter_space=parameter_space,
            random_seed=self.options.random_seed,
        )

        register_optimization_engine(
            services,
            evaluator=optimization_evaluator,
            optimizer_name=self.options.optimizer_name,
            stop_on_error=self.options.stop_on_error,
        )

        register_optimization_workflow(
            services
        )

        register_walkforward_final_report(
            services
        )

        pipeline = register_walkforward_pipeline(
            services,
            pipeline_name=self.options.pipeline_name,
            stop_on_error=self.options.stop_on_error,
        )

        missing = [
            name
            for name in self.REQUIRED_SERVICES
            if not services.contains(name)
        ]

        if missing:
            raise RuntimeError(
                "Walk Forward bootstrap incomplete. Missing: "
                + ", ".join(missing)
            )

        return pipeline
