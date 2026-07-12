"""
BursaAI v6 Sprint 6G.3 Application Runner test.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Bootstrap.application_runner import (
    ApplicationRunner,
)
from Config.app_config import (
    AppConfig,
    ExecutionConfig,
)


class FakeExecutionReport:
    portfolio = {}

    def to_dict(self):
        return {
            "successful": 2,
            "failed": 0,
        }


class FakeExecutionManager:
    def run(self, symbols):
        assert symbols == [
            "1155.KL",
            "1023.KL"
        ]
        return FakeExecutionReport()


class FakeApplication:
    execution_manager = FakeExecutionManager()
    paper_portfolio = None
    performance_engine = None
    walkforward_pipeline = None

    def resolve(self, name):
        return None


def main():
    config = AppConfig(
        execution=ExecutionConfig(
            mode="analysis",
            symbols=[
                "1155.KL",
                "1023.KL",
            ],
            echo_logs=False,
        )
    )

    result = ApplicationRunner(
        application=FakeApplication(),
        config=config,
    ).run()

    assert result["successful"] == 2
    assert result["failed"] == 0

    print("=" * 92)
    print("BURSAAI v6.0 SPRINT 6G.3 RUNNER TEST")
    print("=" * 92)
    print("Application Runner       : OK")
    print("Analysis Mode Dispatch   : OK")
    print("Execution Manager Link   : OK")
    print("Result Serialization     : OK")
    print("=" * 92)
    print("SPRINT 6G.3 APPLICATION RUNNER OK")


if __name__ == "__main__":
    main()
