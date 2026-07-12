"""
=========================================================
BursaAI Engine Result
Version : 6.0 Sprint 1
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from Framework.exceptions import ValidationError


@dataclass(slots=True)
class EngineResult:
    """
    Standard execution result returned by every future BursaAI engine.
    """

    engine: str
    success: bool
    output: Any = None
    duration_ms: float = 0.0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    skipped: bool = False
    started_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    completed_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.engine or not self.engine.strip():
            raise ValidationError("EngineResult requires an engine name.")

        if self.duration_ms < 0:
            raise ValidationError("Engine duration cannot be negative.")

        if self.success and self.errors:
            raise ValidationError(
                "A successful EngineResult cannot contain errors."
            )

    def complete(self, duration_ms: float) -> "EngineResult":
        self.duration_ms = max(float(duration_ms), 0.0)
        self.completed_at = datetime.now(timezone.utc).isoformat()
        self.validate()
        return self

    @classmethod
    def ok(
        cls,
        engine: str,
        output: Any = None,
        duration_ms: float = 0.0,
        warnings: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "EngineResult":
        result = cls(
            engine=engine,
            success=True,
            output=output,
            duration_ms=max(float(duration_ms), 0.0),
            warnings=list(warnings or []),
            metadata=dict(metadata or {}),
            completed_at=datetime.now(timezone.utc).isoformat(),
        )
        result.validate()
        return result

    @classmethod
    def fail(
        cls,
        engine: str,
        error: str,
        duration_ms: float = 0.0,
        warnings: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "EngineResult":
        result = cls(
            engine=engine,
            success=False,
            duration_ms=max(float(duration_ms), 0.0),
            warnings=list(warnings or []),
            errors=[str(error)],
            metadata=dict(metadata or {}),
            completed_at=datetime.now(timezone.utc).isoformat(),
        )
        result.validate()
        return result

    @classmethod
    def skip(
        cls,
        engine: str,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "EngineResult":
        result = cls(
            engine=engine,
            success=True,
            skipped=True,
            warnings=[str(reason)],
            metadata=dict(metadata or {}),
            completed_at=datetime.now(timezone.utc).isoformat(),
        )
        result.validate()
        return result

    def to_dict(self) -> Dict[str, Any]:
        self.validate()

        return {
            "engine": self.engine,
            "success": self.success,
            "output": self.output,
            "duration_ms": round(self.duration_ms, 4),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "skipped": self.skipped,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "metadata": dict(self.metadata),
        }
