"""
=========================================================
BursaAI Historical Engine Report
Version : 6.0 Sprint 6F.2C
=========================================================
"""

from dataclasses import dataclass

from WalkForward.historical_models import HistoricalRunResult


@dataclass(slots=True)
class HistoricalReport:

    result: HistoricalRunResult

    def render_text(self) -> str:

        r = self.result

        status = (
            "SUCCESS"
            if r.successful
            else "WARNING"
        )

        rows = r.metadata.get(
            "dataset_rows",
            0,
        )

        missing = r.metadata.get(
            "missing_intervals",
            0,
        )

        report = [
            "=" * 60,
            "BURSAAI HISTORICAL ENGINE REPORT",
            "=" * 60,
            f"Symbol              : {r.symbol}",
            f"Dataset Rows        : {rows}",
            f"Windows Generated   : {r.windows_generated}",
            f"Splits Created      : {r.splits_created}",
            f"Missing Intervals   : {missing}",
            f"Status              : {status}",
            "=" * 60,
        ]

        return "\n".join(report)