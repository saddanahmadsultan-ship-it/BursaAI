from __future__ import annotations

from importlib import import_module
from time import perf_counter
from typing import Callable, Iterable, List

from Bootstrap.regression_models import RegressionCheck, RegressionResult


class FullRegressionSuite:
    DEFAULT_IMPORTS = [
        "Core.data_loader",
        "Core.indicators",
        "Core.scorer",
        "Core.strategy",
        "Core.decision",
        "Core.dynamic_risk_manager",
        "Core.position_engine",
        "Core.portfolio_allocator",
        "Framework.infrastructure",
        "Framework.execution_manager",
        "Adapters.full_pipeline_registry",
        "Trading.paper_execution",
        "Notifications.notification_hub",
        "Journal.trade_journal",
        "Analytics.performance_engine",
        "WalkForward.pipeline",
        "Bootstrap.service_bootstrap",
        "Config.config_loader",
    ]

    def __init__(self):
        self._checks: List[tuple[str, Callable[[], str]]] = []

    def add_check(self, name: str, check: Callable[[], str]) -> None:
        self._checks.append((str(name), check))

    def add_import_checks(
        self,
        modules: Iterable[str] | None = None,
    ) -> None:
        for module_name in modules or self.DEFAULT_IMPORTS:
            self.add_check(
                f"import:{module_name}",
                lambda name=module_name: self._import(name),
            )

    @staticmethod
    def _import(module_name: str) -> str:
        import_module(module_name)
        return "imported"

    def run(self) -> RegressionResult:
        results = []

        for name, check in self._checks:
            started = perf_counter()

            try:
                details = check() or "OK"

                results.append(
                    RegressionCheck(
                        name=name,
                        success=True,
                        duration_ms=(perf_counter() - started) * 1000,
                        details=str(details),
                    )
                )
            except Exception as error:
                results.append(
                    RegressionCheck(
                        name=name,
                        success=False,
                        duration_ms=(perf_counter() - started) * 1000,
                        error=f"{type(error).__name__}: {error}",
                    )
                )

        return RegressionResult(checks=results)
