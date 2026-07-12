"""
=========================================================
BursaAI Application Runner
Version : 6.0 Sprint 6G.3
=========================================================
"""

from __future__ import annotations

from typing import Any, Dict

from Bootstrap.release_health_report import (
    ReleaseHealthReport,
)
from WalkForward.pipeline_report import (
    WalkForwardPipelineReport,
)


class ApplicationRunner:
    def __init__(
        self,
        application,
        config,
    ):
        self.application = application
        self.config = config

    def run_analysis(self) -> Dict[str, Any]:
        report = self.application.execution_manager.run(
            self.config.execution.symbols
        )

        output = report.to_dict()

        if (
            self.config.features.enable_paper_trading
            and self.application.paper_portfolio is not None
            and report.portfolio
        ):
            contexts = report.portfolio.get(
                "contexts",
                [],
            )

            paper_result = (
                self.application.paper_portfolio
                .open_allocated_positions(
                    contexts
                )
            )

            output["paper_trading"] = (
                paper_result
            )

        if (
            self.config.features.enable_analytics
            and self.application.performance_engine
            is not None
        ):
            output["performance"] = (
                self.application.performance_engine
                .calculate()
                .to_dict()
            )

        return output

    def run_walkforward(self) -> Dict[str, Any]:
        pipeline = (
            self.application.walkforward_pipeline
            or self.application.resolve(
                "walkforward_pipeline"
            )
        )

        if pipeline is None:
            raise RuntimeError(
                "Walk Forward pipeline is not registered."
            )

        result = pipeline.run(
            self.config.walkforward.symbol,
            strategy_name=(
                self.config.walkforward.strategy_name
            ),
            optimization_mode=(
                self.config.walkforward.optimization_mode
            ),
            random_count=(
                self.config.walkforward.random_count
            ),
            export_report=(
                self.config.walkforward.export_report
            ),
            output_directory=(
                self.config.walkforward.output_directory
            ),
        )

        return {
            "result": result.to_dict(),
            "report": WalkForwardPipelineReport(
                result=result
            ).render_text(),
        }

    def run_health(self) -> Dict[str, Any]:
        checker = self.application.resolve(
            "release_health_checker"
        )

        if checker is None:
            raise RuntimeError(
                "Release health checker is not registered."
            )

        required = []

        if self.application.resolve(
            "walkforward_pipeline"
        ) is not None:
            from Bootstrap.walkforward_bootstrap import (
                WalkForwardBootstrap,
            )

            required = (
                WalkForwardBootstrap.REQUIRED_SERVICES
            )

        result = checker.run(
            required_services=required,
            walkforward_dry_run=bool(
                required
            ),
            symbol=(
                self.config.walkforward.symbol
                or "TEST.KL"
            ),
            strategy_name=(
                self.config.walkforward.strategy_name
            ),
            output_directory=(
                self.config.walkforward.output_directory
            ),
        )

        return {
            "result": result.to_dict(),
            "report": ReleaseHealthReport(
                result=result
            ).render_text(),
        }

    def run(self) -> Dict[str, Any]:
        mode = (
            self.config.execution.mode
            .strip()
            .lower()
        )

        if mode in {
            "analysis",
            "paper",
        }:
            return self.run_analysis()

        if mode == "walkforward":
            return self.run_walkforward()

        if mode == "health":
            return self.run_health()

        raise RuntimeError(
            f"Unsupported mode: {mode}"
        )
