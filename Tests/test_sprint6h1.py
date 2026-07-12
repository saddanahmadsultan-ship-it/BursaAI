from pathlib import Path
import sys
import tempfile

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Release.rc_validation_models import (
    RCValidationCheck,
    RCValidationResult,
)
from Release.rc_validation_report import RCValidationReport
from Release.smoke_test import RC1SmokeTest


def main():
    result = RCValidationResult(
        version="6.0.0-rc1",
        checks=[
            RCValidationCheck(
                name="version",
                success=True,
                duration_ms=1.0,
                details="6.0.0-rc1",
            ),
            RCValidationCheck(
                name="config",
                success=True,
                duration_ms=2.0,
                details="valid",
            ),
        ],
    )

    assert result.success is True
    assert result.passed == 2
    assert result.failed == 0

    report = RCValidationReport(result)

    rendered = report.render_text()

    assert (
        "BURSAAI v6.0.0 RC1 VALIDATION REPORT"
        in rendered
    )

    assert "Status  : PASSED" in rendered

    with tempfile.TemporaryDirectory() as folder:
        paths = report.export(folder)

        assert Path(paths["text"]).exists()
        assert Path(paths["json"]).exists()

    smoke = RC1SmokeTest().run()

    assert smoke.modules_checked > 0

    print("=" * 94)
    print("BURSAAI v6.0 SPRINT 6H.1 TEST")
    print("=" * 94)
    print("RC Validation Models      : OK")
    print("RC Validation Report      : OK")
    print("TXT / JSON Export         : OK")
    print("RC Smoke Test             : OK")
    print("=" * 94)
    print("SPRINT 6H.1 RC1 VALIDATION & SMOKE TEST OK")


if __name__ == "__main__":
    main()
