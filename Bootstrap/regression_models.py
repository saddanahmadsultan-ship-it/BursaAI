from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass(slots=True)
class RegressionCheck:
    name: str
    success: bool
    duration_ms: float = 0.0
    details: str = ""
    error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RegressionResult:
    checks: List[RegressionCheck] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return all(check.success for check in self.checks)

    @property
    def passed(self) -> int:
        return sum(1 for check in self.checks if check.success)

    @property
    def failed(self) -> int:
        return len(self.checks) - self.passed

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "passed": self.passed,
            "failed": self.failed,
            "checks": [check.to_dict() for check in self.checks],
        }
