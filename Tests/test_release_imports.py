"""
BursaAI v6 Sprint 6G.2 Release Import Test.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main():
    imports = [
        "Bootstrap.walkforward_bootstrap",
        "Bootstrap.release_health",
        "Bootstrap.release_health_report",
        "Bootstrap.release_bootstrap",
        "WalkForward.pipeline",
        "WalkForward.pipeline_services",
        "WalkForward.final_report_builder",
        "WalkForward.optimization_workflow",
        "WalkForward.historical_engine",
    ]

    for module_name in imports:
        __import__(module_name)

    print("=" * 88)
    print("BURSAAI v6.0 SPRINT 6G.2 RELEASE IMPORT TEST")
    print("=" * 88)
    print(f"Modules Checked : {len(imports)}")
    print("Failed          : 0")
    print("=" * 88)
    print("SPRINT 6G.2 RELEASE IMPORT TEST OK")


if __name__ == "__main__":
    main()
