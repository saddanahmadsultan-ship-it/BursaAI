from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from Release.rc_validation_models import RCValidationResult


@dataclass(slots=True)
class RCValidationReport:
    result: RCValidationResult

    def render_text(self) -> str:
        lines = [
            "=" * 80,
            "BURSAAI v6.0.0 RC1 VALIDATION REPORT",
            "=" * 80,
            f"Version : {self.result.version}",
            f"Status  : {'PASSED' if self.result.success else 'FAILED'}",
            f"Passed  : {self.result.passed}",
            f"Failed  : {self.result.failed}",
            "-" * 80,
        ]

        for check in self.result.checks:
            mark = "OK" if check.success else "FAIL"
            details = check.details if check.success else check.error

            lines.append(
                f"[{mark}] {check.name} | "
                f"{check.duration_ms:.2f} ms | {details}"
            )

        lines.append("=" * 80)

        return "\n".join(lines)

    def export(
        self,
        output_directory: str | Path = "Reports/Release",
    ) -> dict[str, str]:
        output = Path(output_directory)
        output.mkdir(parents=True, exist_ok=True)

        text_path = output / "rc1_validation_report.txt"
        json_path = output / "rc1_validation_report.json"

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
            "text": str(text_path),
            "json": str(json_path),
        }
