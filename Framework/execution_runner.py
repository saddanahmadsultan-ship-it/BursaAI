"""
=========================================================
BursaAI Execution Runner
Version : 6.0 Sprint 6A
=========================================================
"""

from __future__ import annotations

from typing import Callable, Iterable, List, Optional

from Framework.context import AnalysisContext
from Framework.execution_queue import ExecutionQueue
from Framework.execution_state import ExecutionState
from Framework.pipeline import Pipeline


class ExecutionRunner:
    def __init__(
        self,
        pipeline: Pipeline,
        context_factory: Optional[
            Callable[[str], AnalysisContext]
        ] = None,
    ):
        self.pipeline = pipeline
        self.context_factory = (
            context_factory
            or (lambda symbol: AnalysisContext(symbol=symbol))
        )

    def run(
        self,
        symbols: Iterable[str],
        queue: ExecutionQueue,
    ) -> List[AnalysisContext]:
        contexts: List[AnalysisContext] = []

        for symbol in symbols:
            symbol = str(symbol)
            queue.set_state(
                symbol,
                ExecutionState.RUNNING,
            )

            try:
                context = self.context_factory(symbol)
                report = self.pipeline.execute(context)
                contexts.append(context)

                if report.success:
                    queue.set_state(
                        symbol,
                        ExecutionState.COMPLETED,
                    )
                else:
                    queue.set_state(
                        symbol,
                        ExecutionState.FAILED,
                        error=" | ".join(report.errors),
                    )

            except Exception as error:
                queue.set_state(
                    symbol,
                    ExecutionState.FAILED,
                    error=f"{type(error).__name__}: {error}",
                )

        return contexts
