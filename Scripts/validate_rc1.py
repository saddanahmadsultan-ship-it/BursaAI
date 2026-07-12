from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Release.rc_validation_report import RCValidationReport
from Release.rc_validator import RCValidator


def main():
    result = RCValidator(PROJECT_ROOT).run()
    report = RCValidationReport(result)

    print(report.render_text())

    paths = report.export(
        PROJECT_ROOT / "Reports" / "Release"
    )

    print(f"TXT  : {paths['text']}")
    print(f"JSON : {paths['json']}")

    if not result.success:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
