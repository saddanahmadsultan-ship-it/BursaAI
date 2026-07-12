from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from Release.stability_models import (
    StabilityReportResult,
)


@dataclass(slots=True)
class StabilityReport:
    result: StabilityReportResult

    def render_text(self) -> str:
        value = self.result

        lines = [
            "=" * 82,
            "BURSAAI v6.0.0 RC1 STABILITY & FINAL RELEASE GATE",
            "=" * 82,
            f"Version            : {value.version}",
            f"Gate Status        : {value.gate_status}",
            f"Overall Score      : {value.overall_score:.2f}",
            f"Mandatory Passed   : {value.mandatory_passed}",
            f"Recommendation     : {value.recommendation}",
            "-" * 82,
            "EVIDENCE",
            "-" * 82,
        ]

        for item in value.evidence:
            mark = "PASS" if item.passed else "FAIL"

            lines.append(
                f"[{mark}] {item.name:<12} | "
                f"Score {item.score:>6.2f} | "
                f"{item.details}"
            )

        if value.blockers:
            lines.extend(
                [
                    "-" * 82,
                    "BLOCKERS",
                    "-" * 82,
                ]
            )

            for blocker in value.blockers:
                lines.append(
                    f"- {blocker}"
                )

        if value.warnings:
            lines.extend(
                [
                    "-" * 82,
                    "WARNINGS",
                    "-" * 82,
                ]
            )

            for warning in value.warnings:
                lines.append(
                    f"- {warning}"
                )

        lines.append(
            "=" * 82
        )

        return "\n".join(
            lines
        )

    def export(
        self,
        output_directory: str | Path = (
            "Reports/Release"
        ),
    ) -> dict[str, str]:
        output = Path(
            output_directory
        )

        output.mkdir(
            parents=True,
            exist_ok=True,
        )

        text_path = (
            output
            / "rc1_stability_report.txt"
        )

        json_path = (
            output
            / "rc1_stability_report.json"
        )

        text_path.write_text(
            self.render_text() + "\n",
            encoding="utf-8",
        )

        json_path.write_text(
            json.dumps(
                self.result.to_dict(),
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

        return {
            "text": str(
                text_path
            ),
            "json": str(
                json_path
            ),
        }
