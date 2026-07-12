from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


@dataclass(slots=True)
class StabilityEvidence:
    name: str
    available: bool
    passed: bool
    score: float = 0.0
    details: str = ""
    source: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class StabilityReportResult:
    version: str
    generated_at: str
    evidence: List[StabilityEvidence] = field(default_factory=list)
    overall_score: float = 0.0
    mandatory_passed: bool = False
    gate_status: str = "REJECTED"
    recommendation: str = "DO NOT RELEASE"
    blockers: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def approved(self) -> bool:
        return self.gate_status == "APPROVED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "generated_at": self.generated_at,
            "evidence": [item.to_dict() for item in self.evidence],
            "overall_score": round(self.overall_score, 4),
            "mandatory_passed": self.mandatory_passed,
            "gate_status": self.gate_status,
            "recommendation": self.recommendation,
            "approved": self.approved,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
        }
