from __future__ import annotations

from Framework.service_container import ServiceContainer
from Bootstrap.regression_suite import FullRegressionSuite


def register_regression_suite(
    services: ServiceContainer,
) -> FullRegressionSuite:
    suite = FullRegressionSuite()

    services.register_instance(
        "full_regression_suite",
        suite,
        replace=True,
    )

    return suite
