"""
=========================================================
BursaAI Base Engine
Version : 6.0 Sprint 2
=========================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from time import perf_counter
from typing import Optional

from Framework.context import AnalysisContext
from Framework.engine_result import EngineResult
from Framework.exceptions import EngineError
from Framework.metadata import EngineMetadata


class BaseEngine(ABC):
    """
    Standard interface for every BursaAI engine and adapter.
    """

    METADATA = EngineMetadata(
        name="Base Engine",
        version="6.0",
        priority=100,
        enabled=True,
    )

    def __init__(self, metadata: Optional[EngineMetadata] = None):
        self.metadata = metadata or self.METADATA
        self.metadata.validate()

    @property
    def name(self) -> str:
        return self.metadata.name

    @property
    def priority(self) -> int:
        return self.metadata.priority

    @property
    def enabled(self) -> bool:
        return self.metadata.enabled

    @property
    def dependencies(self) -> list[str]:
        return list(self.metadata.dependencies)

    def enable(self) -> None:
        self.metadata.enabled = True

    def disable(self) -> None:
        self.metadata.enabled = False

    def validate_context(self, context: AnalysisContext) -> None:
        if not isinstance(context, AnalysisContext):
            raise EngineError(
                f"{self.name} requires an AnalysisContext instance."
            )

    def pre_process(self, context: AnalysisContext) -> None:
        self.validate_context(context)

    @abstractmethod
    def process(self, context: AnalysisContext):
        """
        Implement engine logic here.

        The method may return:
        - AnalysisContext
        - any output object
        - None
        """

    def post_process(
        self,
        context: AnalysisContext,
        output,
    ) -> None:
        return None

    def execute(self, context: AnalysisContext) -> EngineResult:
        """
        Execute the complete engine lifecycle safely.
        """

        if not self.enabled:
            return EngineResult.skip(
                engine=self.name,
                reason="Engine is disabled.",
                metadata=self.metadata.to_dict(),
            )

        started = perf_counter()

        try:
            self.pre_process(context)

            output = self.process(context)

            self.post_process(context, output)

            duration_ms = (perf_counter() - started) * 1000

            result = EngineResult.ok(
                engine=self.name,
                output=output,
                duration_ms=duration_ms,
                metadata=self.metadata.to_dict(),
            )

            context.add_result(result)

            return result

        except Exception as error:
            duration_ms = (perf_counter() - started) * 1000

            result = EngineResult.fail(
                engine=self.name,
                error=(
                    f"{type(error).__name__}: {error}"
                ),
                duration_ms=duration_ms,
                metadata=self.metadata.to_dict(),
            )

            context.add_result(result)

            return result
