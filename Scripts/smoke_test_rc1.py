from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Release.smoke_test import RC1SmokeTest


def main():
    result = RC1SmokeTest().run()

    print("=" * 72)
    print("BURSAAI v6.0.0 RC1 SMOKE TEST")
    print("=" * 72)
    print(f"Modules checked: {result.modules_checked}")
    print(f"Status         : {'PASSED' if result.success else 'FAILED'}")

    if result.failures:
        print("-" * 72)

        for failure in result.failures:
            print(f"- {failure}")

    print("=" * 72)

    if not result.success:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
