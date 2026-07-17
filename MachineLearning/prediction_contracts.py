from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

@dataclass
class PromotionPrediction:
    candidate_id: str
    probability: float
    calibrated_probability: float
    confidence: float
    predicted_class: int
    decision: str
    reason: str
    model_ids: List[str]
    model_version: str = ""
    cache_hit: bool = False
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    def to_dict(self): return asdict(self)
