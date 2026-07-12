"""
=========================================================
BursaAI Release Bootstrap
Version : 6.0 Sprint 6G.2
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from Bootstrap.release_health import (
    ReleaseHealthChecker,
)
from Bootstrap.service_bootstrap import (
    BootstrapOptions,
    UnifiedServiceBootstrap,
)
from Bootstrap.walkforward_bootstrap import (
    WalkForwardBootstrap,
    WalkForwardBootstrapOptions,
)


@dataclass(slots=True)
class ReleaseBootstrapResult:
    application: object
    walkforward_pipeline: object
    health_checker: ReleaseHealthChecker


class ReleaseBootstrap:
    def __init__(
        self,
        *,
        application_options: Optional[
            BootstrapOptions
        ] = None,
        walkforward_options: Optional[
            WalkForwardBootstrapOptions
        ] = None,
    ):
        self.application_options = (
            application_options
            or BootstrapOptions()
        )

        self.walkforward_options = (
            walkforward_options
            or WalkForwardBootstrapOptions()
        )

    def build(
        self,
        *,
        analysis_functions: dict,
        portfolio_function=None,
        commission_function=None,
        walkforward_loader: Callable,
        window_generator,
        trainer: Callable,
        validator: Callable,
        parameter_space,
        optimization_evaluator: Callable,
    ) -> ReleaseBootstrapResult:
        application = UnifiedServiceBootstrap(
            self.application_options
        ).build(
            portfolio_function=portfolio_function,
            commission_function=commission_function,
            **analysis_functions,
        )

        walkforward_pipeline = (
            WalkForwardBootstrap(
                self.walkforward_options
            ).register(
                application.services,
                loader_function=walkforward_loader,
                window_generator=window_generator,
                trainer=trainer,
                validator=validator,
                parameter_space=parameter_space,
                optimization_evaluator=optimization_evaluator,
            )
        )

        application.walkforward_pipeline = (
            walkforward_pipeline
        )

        checker = ReleaseHealthChecker(
            application
        )

        application.services.register_instance(
            "release_health_checker",
            checker,
            replace=True,
        )

        return ReleaseBootstrapResult(
            application=application,
            walkforward_pipeline=walkforward_pipeline,
            health_checker=checker,
        )
