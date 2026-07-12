"""
=========================================================
BursaAI Release Health Check
Version : 6.0 Sprint 6G.2
=========================================================
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List


@dataclass(slots=True)
class HealthCheckItem:
    name: str
    success: bool
    details: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass(slots=True)
class ReleaseHealthResult:
    checks: List[HealthCheckItem] = field(
        default_factory=list
    )

    @property
    def success(self) -> bool:
        return all(
            check.success
            for check in self.checks
        )

    @property
    def passed(self) -> int:
        return sum(
            1
            for check in self.checks
            if check.success
        )

    @property
    def failed(self) -> int:
        return len(self.checks) - self.passed

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "passed": self.passed,
            "failed": self.failed,
            "checks": [
                check.to_dict()
                for check in self.checks
            ],
        }


class ReleaseHealthChecker:
    def __init__(
        self,
        application_services,
    ):
        self.application = application_services

    def _service_check(
        self,
        name: str,
    ) -> HealthCheckItem:
        success = self.application.services.contains(
            name
        )

        return HealthCheckItem(
            name=f"service:{name}",
            success=success,
            details=(
                "registered"
                if success
                else "missing"
            ),
        )

    def run(
        self,
        *,
        required_services: Iterable[str],
        walkforward_dry_run: bool = False,
        symbol: str = "TEST.KL",
        strategy_name: str = "health_check",
        output_directory: str = "Reports/HealthCheck",
    ) -> ReleaseHealthResult:
        checks = [
            self._service_check(name)
            for name in required_services
        ]

        if walkforward_dry_run:
            try:
                pipeline = self.application.services.resolve(
                    "walkforward_pipeline"
                )

                result = pipeline.run(
                    symbol,
                    strategy_name=strategy_name,
                    export_report=True,
                    output_directory=output_directory,
                )

                checks.append(
                    HealthCheckItem(
                        name="walkforward:dry_run",
                        success=bool(result.success),
                        details=(
                            f"completed_stages="
                            f"{result.completed_stages}, "
                            f"failed_stages="
                            f"{result.failed_stages}"
                        ),
                    )
                )

            except Exception as error:
                checks.append(
                    HealthCheckItem(
                        name="walkforward:dry_run",
                        success=False,
                        details=(
                            f"{type(error).__name__}: {error}"
                        ),
                    )
                )

        return ReleaseHealthResult(
            checks=checks
        )
