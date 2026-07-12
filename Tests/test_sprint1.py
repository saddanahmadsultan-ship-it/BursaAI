"""
BursaAI v6.0 Sprint 1 validation test.

Boleh dijalankan dari:
    BursaAI/
atau:
    BursaAI/Tests/
"""

from pathlib import Path
import sys


# =========================================================
# PROJECT ROOT PATH FIX
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# =========================================================
# FRAMEWORK IMPORTS
# =========================================================

from Framework.context import AnalysisContext
from Framework.domain import AnalysisModel
from Framework.engine_result import EngineResult
from Framework.metadata import EngineMetadata


def main():
    metadata = EngineMetadata(
        name="Sprint 1 Test Engine",
        version="6.0",
        priority=10,
        dependencies=["Indicators"],
    )

    metadata.validate()

    context = AnalysisContext(
        symbol="1155.KL",
        analysis=AnalysisModel(),
    )

    context.analysis.identity.price = 10.50

    context.analysis.score.raw = 80
    context.analysis.score.tradeable = 72
    context.analysis.score.final = 84
    context.analysis.score.grade = "A"

    context.analysis.confidence = 88

    context.analysis.trade.signal = "BUY"

    result = EngineResult.ok(
        engine=metadata.name,
        output={
            "status": "OK",
        },
        duration_ms=12.5,
    )

    context.add_result(result)
    context.complete()
    context.validate()

    legacy = context.to_legacy_dict()

    assert legacy["Code"] == "1155.KL"
    assert legacy["FinalScore"] == 84
    assert legacy["Signal"] == "BUY"

    assert context.successful_engines == 1
    assert context.failed_engines == 0

    print("=" * 64)
    print("BURSAAI v6.0 SPRINT 1 TEST")
    print("=" * 64)
    print("Project Root      : OK")
    print("Metadata          : OK")
    print("Domain Models     : OK")
    print("Analysis Context  : OK")
    print("Engine Result     : OK")
    print("Legacy Bridge     : OK")
    print("=" * 64)
    print("SPRINT 1 FOUNDATION OK")


if __name__ == "__main__":
    main()
