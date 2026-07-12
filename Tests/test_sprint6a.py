"""
BursaAI v6.0 Sprint 6A Execution Framework test.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Framework.base_engine import BaseEngine
from Framework.context import AnalysisContext
from Framework.engine_registry import EngineRegistry
from Framework.event_bus import EventBus
from Framework.execution_manager import ExecutionManager
from Framework.logger import FrameworkLogger
from Framework.metadata import EngineMetadata
from Framework.pipeline import Pipeline
from Framework.pipeline_policy import PipelinePolicy
from Framework.profiler import EngineProfiler


class FakeScoreEngine(BaseEngine):
    METADATA = EngineMetadata(
        name="Fake Score Engine",
        priority=10,
    )

    def process(self, context):
        context.analysis.score.final = (
            90 if context.symbol == "1155.KL" else 70
        )
        context.analysis.confidence = (
            92 if context.symbol == "1155.KL" else 75
        )
        return {"status": "OK"}


class FakePortfolioAllocator:
    def __init__(self, event_bus):
        self.event_bus = event_bus

    def allocate(self, contexts):
        summary = {
            "account_capital": 100000,
            "capital_allocated": 50000,
            "remaining_cash": 50000,
            "portfolio_risk_pct": 2.0,
            "active_positions": len(contexts),
            "status": "ALLOCATED",
        }

        self.event_bus.publish(
            "PortfolioAllocated",
            payload=summary,
            source="Fake Portfolio",
        )

        return {
            "contexts": contexts,
            "results": [],
            "positions": [],
            "summary": summary,
        }


def main():
    event_bus = EventBus()
    events = []

    event_bus.subscribe(
        "*",
        lambda event: events.append(event.name),
    )

    logger = FrameworkLogger(echo=False)
    profiler = EngineProfiler()
    registry = EngineRegistry(
        logger=logger,
        profiler=profiler,
    )
    registry.register(FakeScoreEngine())

    pipeline = Pipeline(
        name="Sprint 6A Test Pipeline",
        registry=registry,
        policy=PipelinePolicy(
            failure_mode="stop",
            validate_dependencies=True,
        ),
        logger=logger,
        profiler=profiler,
    )

    manager = ExecutionManager(
        pipeline=pipeline,
        portfolio_allocator=FakePortfolioAllocator(event_bus),
        event_bus=event_bus,
        pipeline_version="6.0",
    )

    report = manager.run([
        "1155.KL",
        "1023.KL",
    ])

    output = report.to_dict()

    assert report.successful == 2
    assert report.failed == 0
    assert report.average_score == 80.0
    assert report.average_confidence == 83.5
    assert output["portfolio_summary"]["capital_allocated"] == 50000
    assert output["queue_counts"]["COMPLETED"] == 2
    assert "ExecutionStarted" in events
    assert "PortfolioAllocated" in events
    assert "ExecutionCompleted" in events

    print("=" * 88)
    print("BURSAAI v6.0 SPRINT 6A TEST")
    print("=" * 88)
    print("Execution State          : OK")
    print("Execution Queue          : OK")
    print("Execution Session        : OK")
    print("Execution Runner         : OK")
    print("Execution Manager        : OK")
    print("Portfolio Integration    : OK")
    print("Execution Report         : OK")
    print("Execution Events         : OK")
    print("Profiler Integration     : OK")
    print("=" * 88)
    print("SPRINT 6A EXECUTION FRAMEWORK OK")


if __name__ == "__main__":
    main()
