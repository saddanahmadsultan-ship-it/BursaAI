from pathlib import Path
import json
import sys
import tempfile

PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

if str(
    PROJECT_ROOT
) not in sys.path:
    sys.path.insert(
        0,
        str(
            PROJECT_ROOT
        ),
    )

from Release.final_gate import (
    FinalReleaseGate,
)
from Release.stability_report import (
    StabilityReport,
)


def main():
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)

        (
            root
            / "Reports"
            / "Release"
        ).mkdir(
            parents=True,
            exist_ok=True,
        )

        (
            root
            / "Dist"
        ).mkdir(
            parents=True,
            exist_ok=True,
        )

        (
            root
            / "VERSION"
        ).write_text(
            "6.0.0-rc1\n",
            encoding="utf-8",
        )

        regression = {
            "success": True,
            "passed": 20,
            "failed": 0,
        }

        validation = {
            "success": True,
            "passed": 30,
            "failed": 0,
        }

        soak = {
            "success": True,
            "requested": 1000,
            "completed": 1000,
            "failed": 0,
            "duplicate_orders": 0,
            "journal_inconsistencies": 0,
        }

        manifest = {
            "version": "6.0.0-rc1",
            "files": [
                {
                    "path": "main_v6.py",
                    "sha256": "abc",
                    "size_bytes": 10,
                }
            ],
        }

        payloads = {
            "regression": regression,
            "validation": validation,
            "soak": soak,
            "manifest": manifest,
        }

        result = FinalReleaseGate(
            root
        ).evaluate(
            payloads
        )

        assert (
            result.gate_status
            == "APPROVED"
        )

        assert (
            result.mandatory_passed
            is True
        )

        assert (
            result.overall_score
            == 100.0
        )

        assert (
            result.approved
            is True
        )

        report = StabilityReport(
            result
        )

        rendered = (
            report.render_text()
        )

        assert (
            "BURSAAI v6.0.0 RC1 "
            "STABILITY & FINAL RELEASE GATE"
            in rendered
        )

        assert (
            "Gate Status        : APPROVED"
            in rendered
        )

        paths = report.export(
            root
            / "Reports"
            / "Release"
        )

        assert Path(
            paths["text"]
        ).exists()

        assert Path(
            paths["json"]
        ).exists()

    print(
        "=" * 96
    )

    print(
        "BURSAAI v6.0 "
        "SPRINT 6H.3 TEST"
    )

    print(
        "=" * 96
    )

    print(
        "Stability Models          : OK"
    )

    print(
        "Evidence Evaluation       : OK"
    )

    print(
        "Weighted Stability Score  : OK"
    )

    print(
        "Mandatory Gate Rules      : OK"
    )

    print(
        "Approval Decision         : OK"
    )

    print(
        "Stability Report          : OK"
    )

    print(
        "TXT / JSON Export         : OK"
    )

    print(
        "=" * 96
    )

    print(
        "SPRINT 6H.3 RC1 "
        "STABILITY REPORT & "
        "FINAL RELEASE GATE OK"
    )


if __name__ == "__main__":
    main()
