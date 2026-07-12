"""
Sprint 5C.2 real Core import test.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main():
    from Core.position_engine import apply_position_engine
    from Adapters.position_adapter import PositionAdapter

    assert callable(apply_position_engine)

    PositionAdapter(
        position_function=apply_position_engine
    )

    print("=" * 86)
    print("BURSAAI v6.0 SPRINT 5C.2 CORE IMPORT TEST")
    print("=" * 86)
    print("Core.position_engine : OK")
    print("Position Function    : OK")
    print("Position Adapter     : OK")
    print("=" * 86)
    print("SPRINT 5C.2 CORE IMPORTS OK")


if __name__ == "__main__":
    main()
