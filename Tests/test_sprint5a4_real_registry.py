"""
Sprint 5A.4 real Core registration smoke test.

Imports and registers real legacy functions.
No pipeline execution and no market download.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from Adapters.full_pipeline_registry import register_full_analysis_pipeline
from Framework.full_pipeline import build_full_pipeline
from Framework.infrastructure import build_infrastructure


def main():
    infrastructure = build_infrastructure()

    bundle = build_full_pipeline(
        infrastructure,
        echo_logs=False,
    )

    register_full_analysis_pipeline(
        bundle.registry,
        services=infrastructure.services,
    )

    expected = [
        "Loader Adapter",
        "Indicator Adapter",
        "Score Adapter",
        "Trend Adapter",
        "Momentum Adapter",
        "Volume Adapter",
        "Quality Gate Adapter",
        "Smart Money Adapter",
        "Market Regime Adapter",
        "Entry Timing Adapter",
        "AI Brain Adapter",
    ]

    assert bundle.registry.names() == expected
    assert bundle.registry.validate_dependencies() == []

    print("=" * 88)
    print("BURSAAI v6.0 SPRINT 5A.4 REAL REGISTRY TEST")
    print("=" * 88)
    print("Real Core Imports           : OK")
    print("Full Adapter Registration   : OK")
    print("Priority Ordering           : OK")
    print("Dependency Validation       : OK")
    print("Infrastructure Binding      : OK")
    print("=" * 88)
    print("SPRINT 5A.4 REAL REGISTRY OK")


if __name__ == "__main__":
    main()
