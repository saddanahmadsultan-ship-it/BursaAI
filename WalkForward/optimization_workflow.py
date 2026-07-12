"""
=========================================================
BursaAI Optimization Workflow
Version : 6.0 Sprint 6F.6C
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from Framework.event_bus import EventBus
from Framework.service_container import ServiceContainer
from WalkForward.optimization_engine import OptimizationEngine
from WalkForward.optimization_models import OptimizationRunResult
from WalkForward.optimization_report import OptimizationReport
from WalkForward.optimization_summary import (
    build_optimization_summary,
)
from WalkForward.parameter_generator import ParameterGenerator


@dataclass(slots=True)
class OptimizationWorkflowResult:
    run_result: OptimizationRunResult
    summary: Dict[str, Any]
    report_text: str


class OptimizationWorkflow:
    """
    End-to-end workflow:
        ParameterGenerator
        -> OptimizationEngine
        -> Summary
        -> Report
    """

    def __init__(
        self,
        parameter_generator: ParameterGenerator,
        optimization_engine: OptimizationEngine,
        *,
        services: Optional[ServiceContainer] = None,
        event_bus: Optional[EventBus] = None,
    ):
        self.parameter_generator = parameter_generator
        self.optimization_engine = optimization_engine
        self.services = services

        if event_bus is not None:
            self.event_bus = event_bus
        elif (
            services is not None
            and services.contains("event_bus")
        ):
            self.event_bus = services.resolve(
                "event_bus"
            )
        else:
            self.event_bus = None

    def run_grid(
        self,
        *,
        strategy_name: str = "default",
        context: Optional[Dict[str, Any]] = None,
        top_n: int = 5,
    ) -> OptimizationWorkflowResult:
        parameter_sets = (
            self.parameter_generator.generate_grid()
        )

        result = self.optimization_engine.run(
            parameter_sets,
            strategy_name=strategy_name,
            context=context,
        )

        summary = build_optimization_summary(
            result
        )

        report = OptimizationReport(
            result=result,
            top_n=top_n,
        )

        output = OptimizationWorkflowResult(
            run_result=result,
            summary=summary,
            report_text=report.render_text(),
        )

        if self.event_bus is not None:
            self.event_bus.publish(
                "OptimizationWorkflowCompleted",
                payload={
                    "summary": dict(summary),
                    "report_text": output.report_text,
                },
                source="Optimization Workflow",
            )

        return output

    def run_random(
        self,
        count: int,
        *,
        strategy_name: str = "default",
        context: Optional[Dict[str, Any]] = None,
        top_n: int = 5,
    ) -> OptimizationWorkflowResult:
        parameter_sets = (
            self.parameter_generator.generate_random(
                count
            )
        )

        result = self.optimization_engine.run(
            parameter_sets,
            strategy_name=strategy_name,
            context=context,
        )

        summary = build_optimization_summary(
            result
        )

        report = OptimizationReport(
            result=result,
            top_n=top_n,
        )

        output = OptimizationWorkflowResult(
            run_result=result,
            summary=summary,
            report_text=report.render_text(),
        )

        if self.event_bus is not None:
            self.event_bus.publish(
                "OptimizationWorkflowCompleted",
                payload={
                    "summary": dict(summary),
                    "report_text": output.report_text,
                },
                source="Optimization Workflow",
            )

        return output
