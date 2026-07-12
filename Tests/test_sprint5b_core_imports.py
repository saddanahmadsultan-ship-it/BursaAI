"""
Sprint 5B real Core import and registration test.
No market data download.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main():
    from Core.confidence import calculate_confidence
    from Core.strategy import trading_signal
    from Core.decision import make_decision

    from Adapters.confidence_adapter import ConfidenceAdapter
    from Adapters.strategy_adapter import StrategyAdapter
    from Adapters.decision_adapter import DecisionAdapter

    assert callable(calculate_confidence)
    assert callable(trading_signal)
    assert callable(make_decision)

    ConfidenceAdapter(confidence_function=calculate_confidence)
    StrategyAdapter(strategy_function=trading_signal)
    DecisionAdapter(decision_function=make_decision)

    print("=" * 84)
    print("BURSAAI v6.0 SPRINT 5B CORE IMPORT TEST")
    print("=" * 84)
    print("Core.confidence         : OK")
    print("Core.strategy           : OK")
    print("Core.decision           : OK")
    print("Confidence Adapter      : OK")
    print("Strategy Adapter        : OK")
    print("Decision Adapter        : OK")
    print("=" * 84)
    print("SPRINT 5B CORE IMPORTS OK")


if __name__ == "__main__":
    main()
