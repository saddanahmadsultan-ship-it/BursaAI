"""
=========================================================
BursaAI Import Health Checker
Version : 6.0 Sprint 6G.1 Fix 2
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module
from typing import Dict, Iterable, List, Sequence


@dataclass(slots=True)
class ImportCheck:
    module: str
    success: bool
    resolved_module: str = ""
    error: str = ""


@dataclass(slots=True)
class ImportHealthResult:
    checks: List[ImportCheck] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return all(check.success for check in self.checks)

    @property
    def passed(self) -> int:
        return sum(1 for check in self.checks if check.success)

    @property
    def failed(self) -> int:
        return len(self.checks) - self.passed

    def failures(self) -> Dict[str, str]:
        return {
            check.module: check.error
            for check in self.checks
            if not check.success
        }


class ImportHealthChecker:
    """
    Each requirement may be:
    - a module string
    - a tuple/list of alternative module names

    A requirement passes when any candidate imports successfully.
    """

    CORE_MODULES = [
        "Core.data_loader",
        "Core.indicators",
        "Core.scorer",
        "Core.trend_engine",
        "Core.momentum_engine",
        "Core.volume_engine",
        "Core.quality_gate",
        (
            "Core.smart_money_engine",
            "Core.smart_money",
        ),
        (
            "Core.market_regime_engine",
            "Core.market_regime",
        ),
        (
            "Core.entry_timing_engine",
            "Core.entry_timing",
        ),
        (
            "Core.ai_brain",
            "Core.institutional_ai_brain",
        ),
        "Core.confidence",
        "Core.strategy",
        "Core.decision",
        "Core.dynamic_risk_manager",
        "Core.position_engine",
        "Core.portfolio_allocator",
    ]

    FRAMEWORK_MODULES = [
        "Framework.context",
        "Framework.domain",
        "Framework.engine_registry",
        "Framework.pipeline",
        "Framework.infrastructure",
        "Framework.full_pipeline",
        "Framework.execution_manager",
    ]

    ADAPTER_MODULES = [
        "Adapters.loader_adapter",
        "Adapters.indicator_adapter",
        "Adapters.score_adapter",
        "Adapters.trend_adapter",
        "Adapters.momentum_adapter",
        "Adapters.volume_adapter",
        "Adapters.quality_gate_adapter",
        "Adapters.smart_money_adapter",
        "Adapters.market_regime_adapter",
        "Adapters.entry_timing_adapter",
        "Adapters.ai_brain_adapter",
        "Adapters.confidence_adapter",
        "Adapters.strategy_adapter",
        "Adapters.decision_adapter",
        "Adapters.dynamic_risk_adapter",
        "Adapters.position_adapter",
        "Adapters.portfolio_allocator_adapter",
        "Adapters.full_pipeline_registry",
    ]

    PLATFORM_MODULES = [
        "Trading.paper_account",
        "Trading.paper_execution",
        "Trading.paper_portfolio",
        "Notifications.notification_hub",
        "Notifications.telegram_notifier",
        "Journal.trade_journal",
        "Analytics.performance_engine",
        "WalkForward.pipeline",
    ]

    def __init__(
        self,
        modules: Iterable[
            str | Sequence[str]
        ] | None = None,
    ):
        self.modules = list(
            modules
            or (
                self.CORE_MODULES
                + self.FRAMEWORK_MODULES
                + self.ADAPTER_MODULES
                + self.PLATFORM_MODULES
            )
        )

    def _check_requirement(
        self,
        requirement: str | Sequence[str],
    ) -> ImportCheck:
        if isinstance(requirement, str):
            candidates = [requirement]
            label = requirement
        else:
            candidates = list(requirement)
            label = " | ".join(candidates)

        errors = []

        for module_name in candidates:
            try:
                import_module(module_name)

                return ImportCheck(
                    module=label,
                    success=True,
                    resolved_module=module_name,
                )

            except Exception as error:
                errors.append(
                    f"{module_name}: "
                    f"{type(error).__name__}: {error}"
                )

        return ImportCheck(
            module=label,
            success=False,
            error=" || ".join(errors),
        )

    def run(self) -> ImportHealthResult:
        return ImportHealthResult(
            checks=[
                self._check_requirement(requirement)
                for requirement in self.modules
            ]
        )
