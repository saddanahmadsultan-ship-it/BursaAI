from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Release.integrity import IntegrityVerifier


def main():
    manifest = (
        PROJECT_ROOT
        / "Dist"
        / "BursaAI_v6.0.0_rc1_manifest.json"
    )

    result = IntegrityVerifier().verify(
        PROJECT_ROOT,
        manifest,
    )

    print("=" * 76)
    print("BURSAAI v6.0.0 RC1 INTEGRITY CHECK")
    print("=" * 76)
    print(f"Checked   : {result.checked}")
    print(f"Missing   : {len(result.missing)}")
    print(f"Mismatched: {len(result.mismatched)}")
    print(f"Status    : {'VALID' if result.success else 'INVALID'}")
    print("=" * 76)

    if not result.success:
        if result.missing:
            print("Missing:")
            for item in result.missing:
                print(f"- {item}")

        if result.mismatched:
            print("Mismatched:")
            for item in result.mismatched:
                print(f"- {item}")

        raise SystemExit(1)


if __name__ == "__main__":
    main()
