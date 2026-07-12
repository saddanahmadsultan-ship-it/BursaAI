"""
=========================================================
BursaAI Execution Manager
Version : 6.0 Sprint 6A
=========================================================
"""

from __future__ import annotations

from time import perf_counter
from typing import Iterable, Optional

from Adapters.portfolio_allocator_adapter import (
    PortfolioAllocatorAdapter,
)
from Framework.execution_queue import ExecutionQueue
from Framework.execution_report import ExecutionReport
from Framework.execution_runner import ExecutionRunner
from Framework.execution_session import ExecutionSession
from Framework.event_bus import EventBus
from Framework.pipeline import Pipeline


class ExecutionManager:
    """
    Orchestrates:
    - per-stock pipeline
    - execution queue
    - batch portfolio allocation
    - final report
    """

    def __init__(
        self,
        pipeline: Pipeline,
        portfolio_allocator: PortfolioAllocatorAdapter,
        event_bus: Optional[EventBus] = None,
        pipeline_version: str = "6.0",
    ):
        self.pipeline = pipeline
        self.portfolio_allocator = portfolio_allocator
        self.event_bus = event_bus
        self.pipeline_version = pipeline_version

    def run(self, symbols: Iterable[str]) -> ExecutionReport:
        symbols = [str(symbol) for symbol in symbols]
        session = ExecutionSession(
            pipeline_version=self.pipeline_version,
            symbols=symbols,
        )
        queue = ExecutionQueue(symbols)
        runner = ExecutionRunner(self.pipeline)

        started = perf_counter()

        if self.event_bus is not None:
            self.event_bus.publish(
                "ExecutionStarted",
                payload={
                    "run_id": session.run_id,
                    "symbols": symbols,
                },
                source="Execution Manager",
            )

        contexts = runner.run(symbols, queue)

        portfolio = {}
        successful_contexts = [
            context
            for context in contexts
            if not context.failed
        ]

        try:
            if successful_contexts:
                portfolio = self.portfolio_allocator.allocate(
                    successful_contexts
                )
        except Exception as error:
            session.errors.append(
                f"{type(error).__name__}: {error}"
            )

            if self.event_bus is not None:
                self.event_bus.publish(
                    "ExecutionFailed",
                    payload={
                        "run_id": session.run_id,
                        "error": session.errors[-1],
                    },
                    source="Execution Manager",
                )

        duration_ms = (
            perf_counter() - started
        ) * 1000
        session.complete(duration_ms)

        report = ExecutionReport(
            session=session,
            contexts=contexts,
            portfolio=portfolio,
            queue_counts=queue.counts(),
            profiler=self.pipeline.profiler.summary(),
        )

        if self.event_bus is not None:
            self.event_bus.publish(
                "ExecutionCompleted",
                payload=report.to_dict(),
                source="Execution Manager",
            )

        return report
