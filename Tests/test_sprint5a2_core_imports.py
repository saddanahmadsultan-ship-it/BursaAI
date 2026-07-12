"""
Sprint 5A.2 import-only smoke test for the real Core module.

No market data is downloaded.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main():
    from Core.entry_timing_engine import (
        apply_entry_timing_engine,
    )

    from Adapters.entry_timing_adapter import (
        EntryTimingAdapter,
    )

    assert callable(
        apply_entry_timing_engine
    )

    EntryTimingAdapter(
        timing_function=apply_entry_timing_engine
    )

    print("=" * 84)
    print("BURSAAI v6.0 SPRINT 5A.2 CORE IMPORT TEST")
    print("=" * 84)
    print("Core.entry_timing_engine : OK")
    print("Entry Timing Function    : OK")
    print("Entry Timing Adapter     : OK")
    print("=" * 84)
    print("SPRINT 5A.2 CORE IMPORTS OK")


if __name__ == "__main__":
    main()
