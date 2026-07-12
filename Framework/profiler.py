"""
=========================================================
BursaAI Framework Profiler
Version : 6.0 Sprint 2
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

from Framework.engine_result import EngineResult


@dataclass(slots=True)
class ProfileEntry:
    engine: str
    duration_ms: float
    success: bool
    skipped: bool

    def to_dict(self) -> Dict[str, object]:
        return {
            "engine": self.engine,
            "duration_ms": round(
                self.duration_ms,
                4,
            ),
            "success": self.success,
            "skipped": self.skipped,
        }


class EngineProfiler:
    """
    Collect and summarize engine execution duration.
    """

    def __init__(self):
        self.entries: List[ProfileEntry] = []

    def add_result(
        self,
        result: EngineResult,
    ) -> None:
        self.entries.append(
            ProfileEntry(
                engine=result.engine,
                duration_ms=float(
                    result.duration_ms
                ),
                success=bool(result.success),
                skipped=bool(result.skipped),
            )
        )

    def add_results(
        self,
        results: Iterable[EngineResult],
    ) -> None:
        for result in results:
            self.add_result(result)

    @property
    def total_duration_ms(self) -> float:
        return sum(
            entry.duration_ms
            for entry in self.entries
        )

    @property
    def slowest_engine(self) -> str:
        active = [
            entry
            for entry in self.entries
            if not entry.skipped
        ]

        if not active:
            return ""

        return max(
            active,
            key=lambda item: item.duration_ms,
        ).engine

    def summary(self) -> Dict[str, object]:
        successful = sum(
            1
            for entry in self.entries
            if entry.success and not entry.skipped
        )

        failed = sum(
            1
            for entry in self.entries
            if not entry.success
        )

        skipped = sum(
            1
            for entry in self.entries
            if entry.skipped
        )

        return {
            "engine_count": len(self.entries),
            "successful": successful,
            "failed": failed,
            "skipped": skipped,
            "total_duration_ms": round(
                self.total_duration_ms,
                4,
            ),
            "slowest_engine": self.slowest_engine,
            "entries": [
                entry.to_dict()
                for entry in self.entries
            ],
        }

    def reset(self) -> None:
        self.entries.clear()
