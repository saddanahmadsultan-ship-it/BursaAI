"""
Sprint 4C import-only smoke test for real Core modules.

No market data is downloaded.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main():
    from Core.scorer import calculate_score
    from Core.trend_engine import score_trend
    from Core.momentum_engine import score_momentum

    from Adapters.score_adapter import ScoreAdapter
    from Adapters.trend_adapter import TrendAdapter
    from Adapters.momentum_adapter import MomentumAdapter

    assert callable(calculate_score)
    assert callable(score_trend)
    assert callable(score_momentum)

    ScoreAdapter(scorer=calculate_score)
    TrendAdapter(trend_function=score_trend)
    MomentumAdapter(
        momentum_function=score_momentum
    )

    print("=" * 76)
    print("BURSAAI v6.0 SPRINT 4C CORE IMPORT TEST")
    print("=" * 76)
    print("Core.scorer              : OK")
    print("Core.trend_engine        : OK")
    print("Core.momentum_engine     : OK")
    print("Score Adapter            : OK")
    print("Trend Adapter            : OK")
    print("Momentum Adapter         : OK")
    print("=" * 76)
    print("SPRINT 4C CORE IMPORTS OK")


if __name__ == "__main__":
    main()
