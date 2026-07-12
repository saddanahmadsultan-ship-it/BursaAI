from pathlib import Path
import sys

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
from Release.stability_loader import (
    StabilityEvidenceLoader,
)
from Release.stability_report import (
    StabilityReport,
)


def main():
    loader = StabilityEvidenceLoader(
        PROJECT_ROOT
    )

    gate = FinalReleaseGate(
        PROJECT_ROOT
    )

    result = gate.evaluate(
        loader.load_all()
    )

    report = StabilityReport(
        result
    )

    print(
        report.render_text()
    )

    paths = report.export(
        PROJECT_ROOT
        / "Reports"
        / "Release"
    )

    print(
        f"TXT  : {paths['text']}"
    )

    print(
        f"JSON : {paths['json']}"
    )

    if result.gate_status == "REJECTED":
        raise SystemExit(
            1
        )


if __name__ == "__main__":
    main()
