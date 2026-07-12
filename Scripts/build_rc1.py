from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Release.preflight import ReleasePreflight
from Release.rc_builder import ReleaseCandidateBuilder


def main():
    preflight = ReleasePreflight(PROJECT_ROOT).run()

    if not preflight.success:
        print("RC1 build cancelled: preflight failed.")
        raise SystemExit(1)

    result = ReleaseCandidateBuilder().build(
        PROJECT_ROOT,
        PROJECT_ROOT / "Dist",
    )

    print("=" * 76)
    print("BURSAAI v6.0.0 RC1 BUILD COMPLETE")
    print("=" * 76)
    print(f"Archive : {result.archive_path}")
    print(f"Manifest: {result.manifest_path}")
    print(f"Files   : {result.files_added}")
    print(f"Size    : {result.size_bytes:,} bytes")
    print("=" * 76)


if __name__ == "__main__":
    main()
