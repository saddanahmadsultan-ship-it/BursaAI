"""
=========================================================
BursaAI Walk Forward Final Report Services
Version : 6.0 Sprint 6F.7
=========================================================
"""

from __future__ import annotations

from Framework.service_container import (
    ServiceContainer,
)
from WalkForward.final_report_builder import (
    WalkForwardFinalReportBuilder,
)
from WalkForward.final_report_exporter import (
    WalkForwardFinalReportExporter,
)


def register_walkforward_final_report(
    services: ServiceContainer,
) -> WalkForwardFinalReportBuilder:
    builder = WalkForwardFinalReportBuilder()
    exporter = WalkForwardFinalReportExporter()

    services.register_instance(
        "walkforward_final_report_builder",
        builder,
        replace=True,
    )

    services.register_instance(
        "walkforward_final_report_exporter",
        exporter,
        replace=True,
    )

    return builder
