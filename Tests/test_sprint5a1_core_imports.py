"""
Sprint 5A.1 import-only smoke test for the real Core module.

No market data is downloaded.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main():
    from Core.market_regime_engine import (
        apply_market_regime_engine,
    )

    from Adapters.market_regime_adapter import (
        MarketRegimeAdapter,
    )

    assert callable(
        apply_market_regime_engine
    )

    MarketRegimeAdapter(
        regime_function=apply_market_regime_engine
    )

    print("=" * 82)
    print("BURSAAI v6.0 SPRINT 5A.1 CORE IMPORT TEST")
    print("=" * 82)
    print("Core.market_regime_engine : OK")
    print("Market Regime Function    : OK")
    print("Market Regime Adapter     : OK")
    print("=" * 82)
    print("SPRINT 5A.1 CORE IMPORTS OK")


if __name__ == "__main__":
    main()
