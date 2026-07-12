"""
=========================================================
BursaAI Pipeline Execution Layer
Version : 6.0 Sprint 3
=========================================================
"""

from __future__ import annotations

from time import perf_counter
from typing import Callable, Dict, List, Optional, Set

from Framework.context import AnalysisContext
from Framework.engine_registry import EngineRegistry
from Framework.engine_result import EngineResult
from Framework.exceptions import PipelineError
from Framework.logger import FrameworkLogger
from Framework.pipeline_policy import PipelinePolicy
from Framework.pipeline_report import PipelineExecutionReport
from Framework.profiler import EngineProfiler


Hook = Callable[
    [AnalysisContext],
    None,
]


class Pipeline:
    """
    Executes registered engines using a controlled lifecycle.
    """

    def __init__(
        self,
        name: str,
        registry: EngineRegistry,
        policy: Optional[PipelinePolicy] = None,
        logger: Optional[FrameworkLogger] = None,
        profiler: Optional[EngineProfiler] = None,
    ):
        if not name or not name.strip():
            raise PipelineError(
                "Pipeline requires a non-empty name."
            )

        if not isinstance(registry, EngineRegistry):
            raise PipelineError(
                "Pipeline requires an EngineRegistry."
            )

        self.name = name
        self.registry = registry
        self.policy = policy or PipelinePolicy()
        self.policy.validate()

        self.logger = logger or registry.logger
        self.profiler = profiler or registry.profiler

        self._before_hooks: List[Hook] = []
        self._after_hooks: List[Hook] = []

    def add_before_hook(self, hook: Hook) -> None:
        if not callable(hook):
            raise PipelineError(
                "Before hook must be callable."
            )

        self._before_hooks.append(hook)

    def add_after_hook(self, hook: Hook) -> None:
        if not callable(hook):
            raise PipelineError(
                "After hook must be callable."
            )

        self._after_hooks.append(hook)

    def _run_hooks(
        self,
        hooks: List[Hook],
        context: AnalysisContext,
        stage: str,
    ) -> None:
        for hook in hooks:
            try:
                hook(context)
            except Exception as error:
                message = (
                    f"{stage} hook failed: "
                    f"{type(error).__name__}: {error}"
                )

                context.add_error(message)

                self.logger.error(
                    message,
                    engine=self.name,
                )

                if self.policy.failure_mode == "stop":
                    raise PipelineError(message) from error

    def _dependency_map(self) -> Dict[str, Set[str]]:
        return {
            engine.name: set(engine.dependencies)
            for engine in self.registry.ordered_engines()
        }

    def _should_skip_due_to_dependency(
        self,
        engine_name: str,
        failed_or_skipped: Set[str],
        dependency_map: Dict[str, Set[str]],
    ) -> bool:
        dependencies = dependency_map.get(
            engine_name,
            set(),
        )

        return bool(
            dependencies.intersection(
                failed_or_skipped
            )
        )

    def execute(
        self,
        context: AnalysisContext,
    ) -> PipelineExecutionReport:
        if not isinstance(context, AnalysisContext):
            raise PipelineError(
                "Pipeline requires an AnalysisContext."
            )

        started = perf_counter()

        report = PipelineExecutionReport(
            pipeline_name=self.name,
            symbol=context.symbol,
            metadata={
                "failure_mode": self.policy.failure_mode,
                "validate_dependencies": (
                    self.policy.validate_dependencies
                ),
            },
        )

        self.logger.info(
            "Pipeline started.",
            engine=self.name,
        )

        try:
            if self.policy.validate_dependencies:
                dependency_errors = (
                    self.registry.validate_dependencies()
                )

                if dependency_errors:
                    raise PipelineError(
                        "Dependency validation failed: "
                        + " | ".join(dependency_errors)
                    )

            self._run_hooks(
                self._before_hooks,
                context,
                "Before",
            )

            dependency_map = self._dependency_map()
            failed_or_skipped: Set[str] = set()

            for engine in self.registry.ordered_engines():
                if (
                    self.policy.stop_on_context_error
                    and context.failed
                ):
                    report.stopped_early = True
                    report.stop_reason = (
                        "Context contains errors."
                    )
                    break

                if (
                    self.policy.failure_mode
                    == "skip_dependents"
                    and self._should_skip_due_to_dependency(
                        engine.name,
                        failed_or_skipped,
                        dependency_map,
                    )
                ):
                    result = EngineResult.skip(
                        engine=engine.name,
                        reason=(
                            "Skipped because a dependency "
                            "failed or was skipped."
                        ),
                        metadata=engine.metadata.to_dict(),
                    )

                    context.add_result(result)
                    report.add_result(result)
                    self.profiler.add_result(result)

                    failed_or_skipped.add(
                        engine.name
                    )

                    self.logger.warning(
                        "Engine skipped due to dependency.",
                        engine=engine.name,
                    )

                    continue

                if (
                    not engine.enabled
                    and not self.policy.allow_disabled_engines
                ):
                    continue

                self.logger.info(
                    "Engine execution started.",
                    engine=engine.name,
                )

                result = engine.execute(context)

                report.add_result(result)
                self.profiler.add_result(result)

                if result.success:
                    if result.skipped:
                        failed_or_skipped.add(
                            engine.name
                        )

                        self.logger.warning(
                            "Engine skipped.",
                            engine=engine.name,
                        )
                    else:
                        self.logger.info(
                            (
                                "Engine completed in "
                                f"{result.duration_ms:.2f} ms."
                            ),
                            engine=engine.name,
                        )
                else:
                    failed_or_skipped.add(
                        engine.name
                    )

                    self.logger.error(
                        "Engine failed: "
                        + "; ".join(result.errors),
                        engine=engine.name,
                    )

                    if (
                        self.policy.failure_mode
                        == "stop"
                    ):
                        report.stopped_early = True
                        report.stop_reason = (
                            f"Engine failed: {engine.name}"
                        )
                        break

            self._run_hooks(
                self._after_hooks,
                context,
                "After",
            )

        except Exception as error:
            message = (
                f"{type(error).__name__}: {error}"
            )

            report.errors.append(message)
            context.add_error(message)

            report.stopped_early = True
            report.stop_reason = message

            self.logger.error(
                message,
                engine=self.name,
            )

        finally:
            context.complete()

            duration_ms = (
                perf_counter() - started
            ) * 1000

            if self.policy.record_context_snapshot:
                try:
                    report.context_snapshot = (
                        context.summary()
                    )
                except Exception as error:
                    report.warnings.append(
                        "Context snapshot failed: "
                        f"{type(error).__name__}: {error}"
                    )

            report.complete(duration_ms)

            self.logger.info(
                (
                    "Pipeline completed in "
                    f"{duration_ms:.2f} ms."
                ),
                engine=self.name,
            )

        return report
