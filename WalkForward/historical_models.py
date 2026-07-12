from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List
from WalkForward.dataset_splitter import DatasetSplit

@dataclass(slots=True)
class HistoricalRunResult:
    symbol: str
    windows_generated: int
    splits_created: int
    splits: List[DatasetSplit] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)

    @property
    def successful(self) -> bool:
        return self.windows_generated > 0 and self.splits_created > 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "windows_generated": self.windows_generated,
            "splits_created": self.splits_created,
            "successful": self.successful,
            "warnings": list(self.warnings),
            "metadata": dict(self.metadata),
        }
