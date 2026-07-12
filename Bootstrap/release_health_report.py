"""
=========================================================
BursaAI Release Health Report
Version : 6.0 Sprint 6G.2
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from Bootstrap.release_health import (
    ReleaseHealthResult,
)


@dataclass(slots=True)
class ReleaseHealthReport:
    result: ReleaseHealthResult

    def render_text(self) -> str:
        lines = [
            "=" * 72,
            "BURSAAI v6 RELEASE HEALTH CHECK",
            "=" * 72,
            f"Status : {'HEALTHY' if self.result.success else 'FAILED'}",
            f"Passed : {self.result.passed}",
            f"Failed : {self.result.failed}",
            "-" * 72,
        ]

        for check in self.result.checks:
            mark = "OK" if check.success else "FAIL"

            lines.append(
                f"[{mark}] {check.name} - {check.details}"
            )

        lines.append("=" * 72)

        return "\n".join(lines)
