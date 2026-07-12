"""
BursaAI v6 Sprint 6G.1 Full Import Test.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Bootstrap.import_health import (
    ImportHealthChecker,
)


def main():
    result = ImportHealthChecker().run()

    if not result.success:
        print("IMPORT FAILURES")

        for module, error in result.failures().items():
            print(f"- {module}: {error}")

    assert result.success is True

    print("=" * 92)
    print("BURSAAI v6.0 SPRINT 6G.1 FULL IMPORT TEST")
    print("=" * 92)
    print(f"Modules Checked : {len(result.checks)}")
    print(f"Passed          : {result.passed}")
    print(f"Failed          : {result.failed}")
    print("=" * 92)
    print("SPRINT 6G.1 FULL IMPORT TEST OK")


if __name__ == "__main__":
    main()
