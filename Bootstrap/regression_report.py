from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from Bootstrap.regression_models import RegressionResult


@dataclass(slots=True)
class RegressionReport:
    result: RegressionResult

    def render_text(self) -> str:
        lines = [
            "=" * 76,
            "BURSAAI v6 FULL REGRESSION REPORT",
            "=" * 76,
            f"Status : {'PASSED' if self.result.success else 'FAILED'}",
            f"Passed : {self.result.passed}",
            f"Failed : {self.result.failed}",
            "-" * 76,
        ]

        for check in self.result.checks:
            mark = "OK" if check.success else "FAIL"
            suffix = check.details if check.success else check.error

            lines.append(
                f"[{mark}] {check.name} | "
                f"{check.duration_ms:.2f} ms | {suffix}"
            )

        lines.append("=" * 76)

        return "\n".join(lines)

    def export(
        self,
        output_directory: str = "Reports/Release",
    ) -> dict[str, str]:
        output = Path(output_directory)
        output.mkdir(parents=True, exist_ok=True)

        text_path = output / "regression_report.txt"
        json_path = output / "regression_report.json"

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
