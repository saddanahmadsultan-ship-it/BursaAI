"""
Sprint 4D import-only smoke test for real Core modules.

No market data is downloaded.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main():
    from Core.volume_engine import score_volume
    from Core.quality_gate import apply_quality_gate
    from Core.smart_money_engine import apply_smart_money_engine

    from Adapters.volume_adapter import VolumeAdapter
    from Adapters.quality_gate_adapter import QualityGateAdapter
    from Adapters.smart_money_adapter import SmartMoneyAdapter

    assert callable(score_volume)
    assert callable(apply_quality_gate)
    assert callable(apply_smart_money_engine)

    VolumeAdapter(
        volume_function=score_volume
    )

    QualityGateAdapter(
        quality_function=apply_quality_gate
    )

    SmartMoneyAdapter(
        smart_money_function=apply_smart_money_engine
    )

    print("=" * 78)
    print("BURSAAI v6.0 SPRINT 4D CORE IMPORT TEST")
    print("=" * 78)
    print("Core.volume_engine          : OK")
    print("Core.quality_gate           : OK")
    print("Core.smart_money_engine     : OK")
    print("Volume Adapter              : OK")
    print("Quality Gate Adapter        : OK")
    print("Smart Money Adapter         : OK")
    print("=" * 78)
    print("SPRINT 4D CORE IMPORTS OK")


if __name__ == "__main__":
    main()
