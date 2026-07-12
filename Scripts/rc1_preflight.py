from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Release.preflight import ReleasePreflight


def main():
    result = ReleasePreflight(PROJECT_ROOT).run()

    print("=" * 76)
    print("BURSAAI v6.0.0 RC1 PREFLIGHT")
    print("=" * 76)

    for check in result.checks:
        mark = "OK" if check.success else "FAIL"
        print(f"[{mark}] {check.name} - {check.details}")

    print("-" * 76)
    print(f"Passed: {result.passed}")
    print(f"Failed: {result.failed}")
    print(f"Status: {'READY' if result.success else 'NOT READY'}")
    print("=" * 76)

    if not result.success:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
