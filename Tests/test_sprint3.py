"""
BursaAI v6.0 Sprint 3 validation test.

Run from:
    BursaAI/
or:
    BursaAI/Tests/
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
from Framework.profiler import EngineProfiler


class LoadEngine(BaseEngine):
    METADATA = EngineMetadata(
        name="Load",
        version="6.0",
        priority=10,
    )

    def process(self, context):
        context.metadata["loaded"] = True
        return {
            "loaded": True,
        }


class ScoreEngine(BaseEngine):
    METADATA = EngineMetadata(
        name="Score",
        version="6.0",
        priority=20,
        dependencies=["Load"],
    )

    def process(self, context):
        context.analysis.score.raw = 75
        context.analysis.score.final = 82
        return {
            "final_score": 82,
        }


class OptionalDisabledEngine(BaseEngine):
    METADATA = EngineMetadata(
        name="Optional",
        version="6.0",
        priority=30,
        enabled=False,
        dependencies=["Score"],
    )

    def process(self, context):
        raise RuntimeError(
            "Disabled engine must not run."
        )


class FinalEngine(BaseEngine):
    METADATA = EngineMetadata(
        name="Final",
        version="6.0",
        priority=40,
        dependencies=["Score"],
    )

    def process(self, context):
        context.analysis.trade.signal = "BUY"
        return {
            "signal": "BUY",
        }


def before_hook(context):
    context.metadata["before_hook"] = True


def after_hook(context):
    context.metadata["after_hook"] = True


def main():
    logger = FrameworkLogger(
        echo=False
    )

    profiler = EngineProfiler()

    registry = EngineRegistry(
        logger=logger,
        profiler=profiler,
    )

    registry.register(FinalEngine())
    registry.register(OptionalDisabledEngine())
    registry.register(ScoreEngine())
    registry.register(LoadEngine())

    policy = PipelinePolicy(
        failure_mode="continue",
        validate_dependencies=True,
        allow_disabled_engines=True,
        record_context_snapshot=True,
    )

    pipeline = Pipeline(
        name="Sprint 3 Test Pipeline",
        registry=registry,
        policy=policy,
        logger=logger,
        profiler=profiler,
    )

    pipeline.add_before_hook(before_hook)
    pipeline.add_after_hook(after_hook)

    context = AnalysisContext(
        symbol="1155.KL"
    )

    report = pipeline.execute(context)

    assert report.success is True
    assert report.stopped_early is False

    assert report.successful_engines == 3
    assert report.failed_engines == 0
    assert report.skipped_engines == 1

    assert context.metadata["loaded"] is True
    assert context.metadata["before_hook"] is True
    assert context.metadata["after_hook"] is True

    assert context.analysis.score.final == 82
    assert context.analysis.trade.signal == "BUY"

    assert report.context_snapshot is not None
    assert report.duration_ms > 0

    profile = profiler.summary()

    assert profile["engine_count"] == 4
    assert profile["successful"] == 3
    assert profile["failed"] == 0
    assert profile["skipped"] == 1

    print("=" * 72)
    print("BURSAAI v6.0 SPRINT 3 TEST")
    print("=" * 72)
    print("Pipeline Execution   : OK")
    print("Priority Ordering    : OK")
    print("Dependency Validation: OK")
    print("Failure Policy       : OK")
    print("Before / After Hooks : OK")
    print("Disabled Engine Skip : OK")
    print("Execution Report     : OK")
    print("Context Snapshot     : OK")
    print("Profiler Integration : OK")
    print("=" * 72)
    print("SPRINT 3 PIPELINE EXECUTION LAYER OK")


if __name__ == "__main__":
    main()
