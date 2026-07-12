"""
=========================================================
BursaAI Walk Forward Final Report Exporter
Version : 6.0 Sprint 6F.7
=========================================================
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from WalkForward.final_report_models import (
    WalkForwardFinalReportData,
)
from WalkForward.final_report_renderer import (
    WalkForwardFinalReportRenderer,
)


class WalkForwardFinalReportExporter:
    def export(
        self,
        report: WalkForwardFinalReportData,
        *,
        output_directory: str = "Reports/WalkForward",
        basename: str | None = None,
    ) -> Dict[str, str]:
        output = Path(output_directory)

        output.mkdir(
            parents=True,
            exist_ok=True,
        )

        summary = report.summary

        safe_strategy = (
            summary.strategy_name
            .replace(" ", "_")
            .replace("/", "_")
        )

        safe_symbol = (
            summary.symbol
            .replace(".", "_")
            .replace("/", "_")
        )

        name = (
            basename
            or f"{safe_symbol}_{safe_strategy}_walkforward"
        )

        text_path = output / f"{name}.txt"
        json_path = output / f"{name}.json"

        renderer = WalkForwardFinalReportRenderer(
            report=report
        )

        text_path.write_text(
            renderer.render_text() + "\n",
            encoding="utf-8",
        )

        json_path.write_text(
            renderer.render_json(indent=2) + "\n",
            encoding="utf-8",
        )

        return {
            "text": str(text_path),
            "json": str(json_path),
        }
