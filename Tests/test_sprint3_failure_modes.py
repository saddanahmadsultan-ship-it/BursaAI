"""
Additional Sprint 3 failure policy tests.
"""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from Framework.base_engine import BaseEngine
from Framework.context import AnalysisContext
from Framework.engine_registry import EngineRegistry
from Framework.logger import FrameworkLogger
from Framework.metadata import EngineMetadata
from Framework.pipeline import Pipeline
from Framework.pipeline_policy import PipelinePolicy


class GoodEngine(BaseEngine):
    METADATA = EngineMetadata(
        name="Good",
        priority=10,
    )

    def process(self, context):
        context.metadata["good"] = True


class BadEngine(BaseEngine):
    METADATA = EngineMetadata(
        name="Bad",
        priority=20,
        dependencies=["Good"],
    )

    def process(self, context):
        raise RuntimeError("Expected test failure")


class DependentEngine(BaseEngine):
    METADATA = EngineMetadata(
        name="Dependent",
        priority=30,
        dependencies=["Bad"],
    )

    def process(self, context):
        context.metadata["dependent_ran"] = True


def build_registry():
    logger = FrameworkLogger(echo=False)
    registry = EngineRegistry(logger=logger)

    registry.register(GoodEngine())
    registry.register(BadEngine())
    registry.register(DependentEngine())

    return registry, logger


def test_stop_mode():
    registry, logger = build_registry()

    pipeline = Pipeline(
        name="Stop Mode",
        registry=registry,
        policy=PipelinePolicy(
            failure_mode="stop"
        ),
        logger=logger,
    )

    report = pipeline.execute(
        AnalysisContext(symbol="TEST.KL")
    )

    assert report.stopped_early is True
    assert report.failed_engines == 1
    assert len(report.engine_results) == 2


def test_skip_dependents_mode():
    registry, logger = build_registry()

    pipeline = Pipeline(
        name="Skip Dependents",
        registry=registry,
        policy=PipelinePolicy(
            failure_mode="skip_dependents"
        ),
        logger=logger,
    )

    context = AnalysisContext(
        symbol="TEST.KL"
    )

    report = pipeline.execute(context)

    assert report.stopped_early is False
    assert report.failed_engines == 1
    assert report.skipped_engines == 1
    assert "dependent_ran" not in context.metadata


def main():
    test_stop_mode()
    test_skip_dependents_mode()

    print("=" * 72)
    print("SPRINT 3 FAILURE MODES")
    print("=" * 72)
    print("Stop on Error       : OK")
    print("Skip Dependents     : OK")
    print("=" * 72)
    print("SPRINT 3 FAILURE POLICY TESTS OK")


if __name__ == "__main__":
    main()
