"""
=========================================================
BursaAI Framework Configuration
Version : 6.0 Sprint 5A.0
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(slots=True)
class FrameworkConfiguration:
    environment: str = "development"
    enable_events: bool = True
    enable_cache: bool = True
    enable_plugins: bool = True
    cache_default_ttl: float = 300.0
    log_level: str = "INFO"
    extra: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        valid_environments = {
            "development",
            "testing",
            "production",
        }

        if self.environment not in valid_environments:
            raise ValueError(
                "Invalid environment."
            )

        if self.cache_default_ttl < 0:
            raise ValueError(
                "cache_default_ttl cannot be negative."
            )

    def to_dict(self) -> Dict[str, Any]:
        self.validate()

        return {
            "environment": self.environment,
            "enable_events": self.enable_events,
            "enable_cache": self.enable_cache,
            "enable_plugins": self.enable_plugins,
            "cache_default_ttl": self.cache_default_ttl,
            "log_level": self.log_level,
            "extra": dict(self.extra),
        }
