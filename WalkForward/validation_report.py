"""
=========================================================
BursaAI Validation Run Report
Version : 6.0 Sprint 6F.4
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from WalkForward.validation_models import ValidationRunResult


@dataclass(slots=True)
class ValidationReport:
    result: ValidationRunResult

    def render_text(self) -> str:
        value = self.result

        return "\n".join(
            [
                "=" * 60,
                "BURSAAI VALIDATION WINDOW REPORT",
                "=" * 60,
                f"Symbol              : {value.symbol}",
                f"Total Windows       : {value.total_windows}",
                f"Successful Windows  : {value.successful_windows}",
                f"Failed Windows      : {value.failed_windows}",
                f"Duration            : {value.duration_ms:.2f} ms",
                f"Status              : "
                f"{'SUCCESS' if value.success else 'PARTIAL/FAILED'}",
                "=" * 60,
            ]
        )
