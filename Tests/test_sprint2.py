"""
BursaAI v6.0 Sprint 2 validation test.

Run from either:
    BursaAI/
or:
    BursaAI/Tests/
"""

from pathlib import Path
import sys
from time import sleep


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from Framework.base_engine import BaseEngine
from Framework.context import AnalysisContext
from Framework.engine_registry import EngineRegistry
from Framework.logger import FrameworkLogger
from Framework.metadata import EngineMetadata
from Framework.profiler import EngineProfiler


class FirstTestEngine(BaseEngine):
    METADATA = EngineMetadata(
        name="First Test Engine",
        version="6.0",
        priority=10,
    )

    def process(self, context):
        sleep(0.01)
        context.analysis.score.raw = 70
        context.add_log("First engine completed.")
        return {
            "raw_score": 70,
        }


class SecondTestEngine(BaseEngine):
    METADATA = EngineMetadata(
        name="Second Test Engine",
        version="6.0",
        priority=20,
        dependencies=[
            "First Test Engine",
        ],
    )

    def process(self, context):
        sleep(0.005)
        context.analysis.score.final = (
            context.analysis.score.raw + 10
        )
        context.add_log("Second engine completed.")
        return {
            "final_score": 80,
        }


class FailingTestEngine(BaseEngine):
    METADATA = EngineMetadata(
        name="Failing Test Engine",
        version="6.0",
        priority=30,
        enabled=False,
    )

    def process(self, context):
        raise RuntimeError("This should not execute.")


def main():
    logger = FrameworkLogger(
        echo=False
    )

    profiler = EngineProfiler()

    registry = EngineRegistry(
        logger=logger,
        profiler=profiler,
    )

    registry.register(
        SecondTestEngine()
    )

    registry.register(
        FirstTestEngine()
    )

    registry.register(
        FailingTestEngine()
    )

    context = AnalysisContext(
        symbol="1155.KL"
    )

    results = registry.run(context)

    assert registry.names() == [
        "First Test Engine",
        "Second Test Engine",
        "Failing Test Engine",
    ]

    assert len(results) == 3

    assert results[0].success is True
    assert results[0].skipped is False

    assert results[1].success is True
    assert results[1].skipped is False

    assert results[2].success is True
    assert results[2].skipped is True

    assert context.analysis.score.raw == 70
    assert context.analysis.score.final == 80

    profile = profiler.summary()

    assert profile["engine_count"] == 3
    assert profile["successful"] == 2
    assert profile["failed"] == 0
    assert profile["skipped"] == 1
    assert profile["total_duration_ms"] > 0

    assert len(logger.records) >= 6

    print("=" * 68)
    print("BURSAAI v6.0 SPRINT 2 TEST")
    print("=" * 68)
    print("BaseEngine         : OK")
    print("Engine Registry    : OK")
    print("Priority Ordering  : OK")
    print("Dependency Check   : OK")
    print("Enable / Disable   : OK")
    print("Central Logger     : OK")
    print("Engine Profiler    : OK")
    print("Context Integration: OK")
    print("=" * 68)
    print("SPRINT 2 ENGINE FOUNDATION OK")


if __name__ == "__main__":
    main()
