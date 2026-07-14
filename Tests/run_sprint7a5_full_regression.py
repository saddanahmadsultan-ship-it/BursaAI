from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

TEST_MODULES = [
    "Tests.test_sprint7a5_rc1",
    "Tests.test_sprint7a5_rc2",
    "Tests.test_sprint7a5_rc3",
    "Tests.test_sprint7a5_rc4",
    "Tests.test_sprint7a5_final_rc",
]


def main() -> int:
    for module in TEST_MODULES:
        print("=" * 72)
        print("RUNNING", module)
        print("=" * 72)

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "unittest",
                module,
                "-v",
            ],
            cwd=PROJECT_ROOT,
        )

        if result.returncode != 0:
            print("REGRESSION FAILED:", module)
            return result.returncode

    print("=" * 72)
    print("SPRINT 7A.5 FULL REGRESSION PASSED")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
