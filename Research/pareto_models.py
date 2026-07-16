from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict


@dataclass
class ParetoPoint:
    candidate_id: str
    result_id: str
    front: int
    domination_count: int
    dominates_count: int
    crowding_distance: float
    objectives: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
