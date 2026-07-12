"""
=========================================================
BursaAI Application Services
Version : 6.0 Sprint 6G.1
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(slots=True)
class ApplicationServices:
    infrastructure: Any
    analysis_bundle: Any = None
    portfolio_allocator: Any = None
    execution_manager: Any = None
    paper_portfolio: Any = None
    notification_hub: Any = None
    trade_journal: Any = None
    performance_engine: Any = None
    walkforward_pipeline: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def services(self):
        return self.infrastructure.services

    @property
    def events(self):
        return self.infrastructure.events

    def resolve(
        self,
        name: str,
        default: Optional[Any] = None,
    ) -> Any:
        if self.services.contains(name):
            return self.services.resolve(name)

        return default

    def service_names(self) -> list[str]:
        if hasattr(self.services, "names"):
            return list(self.services.names())

        if hasattr(self.services, "_services"):
            return sorted(
                str(name)
                for name in self.services._services
            )

        return []
