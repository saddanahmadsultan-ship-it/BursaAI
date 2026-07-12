from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module
from pathlib import Path
from typing import List


@dataclass(slots=True)
class SmokeTestResult:
    success: bool
    modules_checked: int
    failures: List[str] = field(default_factory=list)


class RC1SmokeTest:
    MODULES = [
        "Config.app_config",
        "Config.config_loader",
        "Framework.infrastructure",
        "Framework.execution_manager",
        "Adapters.full_pipeline_registry",
        "Trading.paper_account",
        "Trading.paper_execution",
        "Notifications.notification_hub",
        "Journal.trade_journal",
        "Analytics.performance_engine",
        "WalkForward.pipeline",
        "Bootstrap.service_bootstrap",
        "Bootstrap.release_health",
        "Release.preflight",
        "Release.rc_builder",
    ]

    def run(self) -> SmokeTestResult:
        failures = []

        for module_name in self.MODULES:
            try:
                import_module(module_name)
            except Exception as error:
                failures.append(
                    f"{module_name}: "
                    f"{type(error).__name__}: {error}"
                )

        return SmokeTestResult(
            success=not failures,
            modules_checked=len(self.MODULES),
            failures=failures,
        )
