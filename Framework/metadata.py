"""
=========================================================
BursaAI Engine Metadata
Version : 6.0 Sprint 1
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from Framework.exceptions import ValidationError


@dataclass(slots=True)
class EngineMetadata:
    """
    Standard metadata for every BursaAI engine or adapter.
    """

    name: str
    version: str = "1.0"
    author: str = "BursaAI"
    priority: int = 100
    enabled: bool = True
    dependencies: List[str] = field(default_factory=list)
    description: str = ""
    category: str = "analysis"
    tags: List[str] = field(default_factory=list)
    extra: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.name or not self.name.strip():
            raise ValidationError("Engine metadata requires a non-empty name.")

        if self.priority < 0:
            raise ValidationError("Engine priority cannot be negative.")

        if not isinstance(self.dependencies, list):
            raise ValidationError("Engine dependencies must be a list.")

    def to_dict(self) -> Dict[str, Any]:
        self.validate()

        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "priority": self.priority,
            "enabled": self.enabled,
            "dependencies": list(self.dependencies),
            "description": self.description,
            "category": self.category,
            "tags": list(self.tags),
            "extra": dict(self.extra),
        }
