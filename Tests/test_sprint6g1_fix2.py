"""
BursaAI v6 Sprint 6G.1 Fix 2 module-name compatibility test.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Bootstrap.import_health import ImportHealthChecker


def main():
    direct = ImportHealthChecker(
        modules=[
            (
                "Core.smart_money_engine",
                "Core.smart_money",
            ),
            (
                "Core.market_regime_engine",
                "Core.market_regime",
            ),
            (
                "Core.entry_timing_engine",
                "Core.entry_timing",
            ),
        ]
    ).run()

    if not direct.success:
        for module, error in direct.failures().items():
            print(f"- {module}: {error}")

    assert direct.success is True

    resolved = [
        check.resolved_module
        for check in direct.checks
    ]

    assert "Core.smart_money_engine" in resolved
    assert "Core.market_regime_engine" in resolved
    assert "Core.entry_timing_engine" in resolved

    full = ImportHealthChecker().run()

    if not full.success:
        print("REMAINING IMPORT FAILURES")

        for module, error in full.failures().items():
            print(f"- {module}: {error}")

    assert full.success is True

    print("=" * 94)
    print("BURSAAI v6.0 SPRINT 6G.1 FIX 2 TEST")
    print("=" * 94)
    print("Smart Money Module Alias  : OK")
    print("Market Regime Module Alias: OK")
    print("Entry Timing Module Alias : OK")
    print("Alternative Import Logic  : OK")
    print("Full Import Health        : OK")
    print("=" * 94)
    print("SPRINT 6G.1 MODULE NAME FIX OK")


if __name__ == "__main__":
    main()
