"""
=========================================================
BursaAI Unified Service Bootstrap
Version : 6.0 Sprint 6G.1
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

from Adapters.full_pipeline_registry import (
    register_full_analysis_pipeline,
)
from Adapters.portfolio_registry import (
    register_portfolio_allocator,
)
from Analytics.performance_services import (
    register_performance_analytics,
)
from Bootstrap.application_services import (
    ApplicationServices,
)
from Bootstrap.service_collision import (
    ServiceCollisionGuard,
)
from Bootstrap.service_manifest import (
    SERVICE_GROUPS,
)
from Framework.execution_manager import (
    ExecutionManager,
)
from Framework.full_pipeline import (
    build_full_pipeline,
)
from Framework.infrastructure import (
    build_infrastructure,
)
from Journal.journal_services import (
    register_trade_journal,
)
from Notifications.notification_services import (
    register_notification_hub,
)
from Trading.paper_services import (
    register_paper_trading,
)


@dataclass(slots=True)
class BootstrapOptions:
    enable_paper_trading: bool = True
    enable_notifications: bool = True
    enable_journal: bool = True
    enable_analytics: bool = True
    enable_walkforward: bool = False

    starting_capital: float = 100000.0
    journal_database_path: str = (
        "Data/bursaai_journal.db"
    )

    telegram_enabled: bool = False
    telegram_dry_run: bool = True

    pipeline_failure_mode: str = "stop"
    echo_logs: bool = False


class UnifiedServiceBootstrap:
    def __init__(
        self,
        options: Optional[
            BootstrapOptions
        ] = None,
    ):
        self.options = (
            options
            or BootstrapOptions()
        )

    def validate_manifest(self) -> None:
        result = ServiceCollisionGuard().check(
            SERVICE_GROUPS
        )

        if not result.success:
            raise RuntimeError(
                "Service manifest collision: "
                + "; ".join(result.collisions)
            )

    def build(
        self,
        *,
        data_loader=None,
        indicator_function=None,
        scorer=None,
        trend_function=None,
        momentum_function=None,
        volume_function=None,
        quality_function=None,
        smart_money_function=None,
        regime_function=None,
        timing_function=None,
        brain_function=None,
        confidence_function=None,
        strategy_function=None,
        decision_function=None,
        risk_function=None,
        position_function=None,
        portfolio_function=None,
        commission_function=None,
    ) -> ApplicationServices:
        self.validate_manifest()

        infrastructure = build_infrastructure()

        analysis_bundle = build_full_pipeline(
            infrastructure,
            name="BursaAI v6 Unified Analysis Pipeline",
            failure_mode=self.options.pipeline_failure_mode,
            echo_logs=self.options.echo_logs,
        )

        register_full_analysis_pipeline(
            analysis_bundle.registry,
            data_loader=data_loader,
            indicator_function=indicator_function,
            scorer=scorer,
            trend_function=trend_function,
            momentum_function=momentum_function,
            volume_function=volume_function,
            quality_function=quality_function,
            smart_money_function=smart_money_function,
            regime_function=regime_function,
            timing_function=timing_function,
            brain_function=brain_function,
            confidence_function=confidence_function,
            strategy_function=strategy_function,
            decision_function=decision_function,
            risk_function=risk_function,
            position_function=position_function,
            services=infrastructure.services,
        )

        portfolio_allocator = register_portfolio_allocator(
            infrastructure.services,
            allocator_function=portfolio_function,
        )

        execution_manager = ExecutionManager(
            pipeline=analysis_bundle.pipeline,
            portfolio_allocator=portfolio_allocator,
            event_bus=infrastructure.events,
            pipeline_version="6.0",
        )

        infrastructure.services.register_instance(
            "execution_manager",
            execution_manager,
            replace=True,
        )

        paper_portfolio = None
        notification_hub = None
        trade_journal = None
        performance_engine = None

        if self.options.enable_paper_trading:
            paper_portfolio = register_paper_trading(
                infrastructure.services,
                starting_capital=self.options.starting_capital,
                commission_function=commission_function,
            )

        if self.options.enable_notifications:
            notification_hub = register_notification_hub(
                infrastructure.services,
                telegram_enabled=(
                    self.options.telegram_enabled
                ),
                telegram_dry_run=(
                    self.options.telegram_dry_run
                ),
            )

        if self.options.enable_journal:
            trade_journal = register_trade_journal(
                infrastructure.services,
                database_path=(
                    self.options.journal_database_path
                ),
            )

        if (
            self.options.enable_analytics
            and trade_journal is not None
        ):
            performance_engine = (
                register_performance_analytics(
                    infrastructure.services,
                    starting_capital=(
                        self.options.starting_capital
                    ),
                )
            )

        application = ApplicationServices(
            infrastructure=infrastructure,
            analysis_bundle=analysis_bundle,
            portfolio_allocator=portfolio_allocator,
            execution_manager=execution_manager,
            paper_portfolio=paper_portfolio,
            notification_hub=notification_hub,
            trade_journal=trade_journal,
            performance_engine=performance_engine,
            metadata={
                "version": "6.0",
                "bootstrap": "Sprint 6G.1",
            },
        )

        infrastructure.services.register_instance(
            "application_services",
            application,
            replace=True,
        )

        return application
