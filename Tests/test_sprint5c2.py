"""
BursaAI v6.0 Sprint 5C.2 Position Adapter test.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Adapters.position_adapter import PositionAdapter
from Framework.context import AnalysisContext
from Framework.infrastructure import build_infrastructure


def fake_position_engine(result):
    output = dict(result)
    output.update({
        "AccountCapital": 100000.0,
        "RiskPercent": 0.72,
        "RiskCapital": 720.0,
        "RiskPerShare": 0.40,
        "Shares": 1800,
        "Lots": 18,
        "Capital": 18720.0,
        "CapitalUsed": 18720.0,
        "RemainingCapital": 81280.0,
        "Allocation": 18.72,
        "ActualRiskPercent": 0.72,
        "MaxLoss": 720.0,
        "PotentialProfit": 1440.0,
        "PositionStatus": "READY",
        "PositionRating": "STRONG",
    })
    return output


def main():
    infrastructure = build_infrastructure()

    events = []
    infrastructure.events.subscribe(
        "PositionCalculated",
        lambda event: events.append(event),
    )

    context = AnalysisContext(symbol="1155.KL")
    context.analysis.position.risk_percent = 0.72

    adapter = PositionAdapter(
        position_function=fake_position_engine,
        services=infrastructure.services,
    )

    result = adapter.execute(context)

    assert result.success is True
    assert context.analysis.position.account_capital == 100000.0
    assert context.analysis.position.risk_percent == 0.72
    assert context.analysis.position.risk_capital == 720.0
    assert context.analysis.position.risk_per_share == 0.40
    assert context.analysis.position.shares == 1800
    assert context.analysis.position.lots == 18
    assert context.analysis.position.capital_used == 18720.0
    assert context.analysis.position.remaining_capital == 81280.0
    assert context.analysis.position.allocation_percent == 18.72
    assert context.analysis.position.actual_risk_percent == 0.72
    assert context.analysis.position.max_loss == 720.0
    assert context.analysis.position.potential_profit == 1440.0
    assert context.analysis.position.status == "READY"
    assert context.analysis.position.rating == "STRONG"

    assert len(events) == 1
    assert events[0].payload["shares"] == 1800
    assert events[0].payload["status"] == "READY"

    print("=" * 86)
    print("BURSAAI v6.0 SPRINT 5C.2 TEST")
    print("=" * 86)
    print("Position Adapter          : OK")
    print("Position Model Sync       : OK")
    print("Capital Sync              : OK")
    print("Risk Sync                 : OK")
    print("Shares / Lots Sync        : OK")
    print("Profit / Loss Sync        : OK")
    print("Position Event            : OK")
    print("=" * 86)
    print("SPRINT 5C.2 POSITION ADAPTER OK")


if __name__ == "__main__":
    main()
