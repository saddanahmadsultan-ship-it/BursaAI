"""
=========================================================
BursaAI Service Collision Guard
Version : 6.0 Sprint 6G.1
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass(slots=True)
class ServiceCollisionResult:
    collisions: List[str] = field(
        default_factory=list
    )

    @property
    def success(self) -> bool:
        return not self.collisions


class ServiceCollisionGuard:
    """
    Detect duplicate planned service names before registration.
    """

    def check(
        self,
        service_groups: dict[str, list[str]],
    ) -> ServiceCollisionResult:
        seen = {}
        collisions = []

        for group, names in service_groups.items():
            for name in names:
                if name in seen:
                    collisions.append(
                        f"{name}: {seen[name]} / {group}"
                    )
                else:
                    seen[name] = group

        return ServiceCollisionResult(
            collisions=collisions
        )
