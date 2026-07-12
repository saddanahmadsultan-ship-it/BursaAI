from __future__ import annotations

from typing import Any, Dict, Iterable


class ReleaseDryRun:
    def __init__(self, application):
        self.application = application

    def run_analysis(
        self,
        symbols: Iterable[str],
    ) -> Dict[str, Any]:
        report = self.application.execution_manager.run(list(symbols))

        return {
            "execution": report.to_dict(),
            "portfolio": report.portfolio,
        }

    def run_performance(self) -> Dict[str, Any]:
        engine = self.application.performance_engine

        if engine is None:
            return {
                "skipped": True,
                "reason": "Performance Analytics disabled",
            }

        return engine.calculate().to_dict()

    def run_walkforward(
        self,
        *,
        symbol: str,
        strategy_name: str,
        output_directory: str,
    ) -> Dict[str, Any]:
        pipeline = (
            self.application.walkforward_pipeline
            or self.application.resolve("walkforward_pipeline")
        )

        if pipeline is None:
            return {
                "skipped": True,
                "reason": "Walk Forward pipeline not registered",
            }

        result = pipeline.run(
            symbol,
            strategy_name=strategy_name,
            export_report=True,
            output_directory=output_directory,
        )

        return result.to_dict()
