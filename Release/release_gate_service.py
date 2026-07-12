from __future__ import annotations

from Framework.service_container import (
    ServiceContainer,
)
from Release.final_gate import (
    FinalReleaseGate,
)
from Release.stability_loader import (
    StabilityEvidenceLoader,
)


class ReleaseGateService:
    def __init__(
        self,
        project_root,
    ):
        self.project_root = project_root
        self.loader = (
            StabilityEvidenceLoader(
                project_root
            )
        )
        self.gate = FinalReleaseGate(
            project_root
        )

    def evaluate(self):
        return self.gate.evaluate(
            self.loader.load_all()
        )


def register_release_gate(
    services: ServiceContainer,
    *,
    project_root,
) -> ReleaseGateService:
    gate = ReleaseGateService(
        project_root
    )

    services.register_instance(
        "release_gate_service",
        gate,
        replace=True,
    )

    return gate
