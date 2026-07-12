"""
=========================================================
BursaAI Engine Registry
Version : 6.0 Sprint 2
=========================================================
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from Framework.base_engine import BaseEngine
from Framework.context import AnalysisContext
from Framework.engine_result import EngineResult
from Framework.exceptions import RegistryError
from Framework.logger import FrameworkLogger
from Framework.profiler import EngineProfiler


class EngineRegistry:
    """
    Store, order and execute BursaAI engines.
    """

    def __init__(
        self,
        logger: Optional[FrameworkLogger] = None,
        profiler: Optional[EngineProfiler] = None,
    ):
        self._engines: Dict[str, BaseEngine] = {}
        self.logger = logger or FrameworkLogger(
            echo=False
        )
        self.profiler = profiler or EngineProfiler()

    def register(
        self,
        engine: BaseEngine,
        replace: bool = False,
    ) -> None:
        if not isinstance(engine, BaseEngine):
            raise RegistryError(
                "Only BaseEngine instances can be registered."
            )

        name = engine.name

        if name in self._engines and not replace:
            raise RegistryError(
                f"Engine already registered: {name}"
            )

        self._engines[name] = engine

        self.logger.info(
            "Engine registered.",
            engine=name,
        )

    def unregister(self, name: str) -> None:
        if name not in self._engines:
            raise RegistryError(
                f"Engine not found: {name}"
            )

        del self._engines[name]

        self.logger.info(
            "Engine unregistered.",
            engine=name,
        )

    def get(self, name: str) -> BaseEngine:
        if name not in self._engines:
            raise RegistryError(
                f"Engine not found: {name}"
            )

        return self._engines[name]

    def contains(self, name: str) -> bool:
        return name in self._engines

    def enable(self, name: str) -> None:
        self.get(name).enable()

    def disable(self, name: str) -> None:
        self.get(name).disable()

    def names(self) -> List[str]:
        return [
            engine.name
            for engine in self.ordered_engines()
        ]

    def ordered_engines(self) -> List[BaseEngine]:
        return sorted(
            self._engines.values(),
            key=lambda engine: (
                engine.priority,
                engine.name,
            ),
        )

    def validate_dependencies(self) -> List[str]:
        """
        Return dependency errors without executing engines.
        """

        registered = set(self._engines)
        errors: List[str] = []

        for engine in self.ordered_engines():
            missing = [
                dependency
                for dependency in engine.dependencies
                if dependency not in registered
            ]

            if missing:
                errors.append(
                    f"{engine.name}: missing dependencies "
                    f"{', '.join(missing)}"
                )

        return errors

    def run(
        self,
        context: AnalysisContext,
        stop_on_error: bool = False,
        validate_dependencies: bool = True,
    ) -> List[EngineResult]:
        if not isinstance(context, AnalysisContext):
            raise RegistryError(
                "Registry requires an AnalysisContext."
            )

        if validate_dependencies:
            dependency_errors = (
                self.validate_dependencies()
            )

            if dependency_errors:
                raise RegistryError(
                    "Dependency validation failed: "
                    + " | ".join(dependency_errors)
                )

        results: List[EngineResult] = []

        for engine in self.ordered_engines():
            self.logger.info(
                "Execution started.",
                engine=engine.name,
            )

            result = engine.execute(context)

            results.append(result)
            self.profiler.add_result(result)

            if result.success:
                if result.skipped:
                    self.logger.warning(
                        "Engine skipped.",
                        engine=engine.name,
                    )
                else:
                    self.logger.info(
                        (
                            "Execution completed in "
                            f"{result.duration_ms:.2f} ms."
                        ),
                        engine=engine.name,
                    )
            else:
                self.logger.error(
                    "Execution failed: "
                    + "; ".join(result.errors),
                    engine=engine.name,
                )

                if stop_on_error:
                    break

        return results

    def clear(self) -> None:
        self._engines.clear()
        self.profiler.reset()
        self.logger.clear()

    def __len__(self) -> int:
        return len(self._engines)

    def __iter__(self) -> Iterable[BaseEngine]:
        return iter(self.ordered_engines())
