"""
=========================================================
BursaAI Validation Dataset Model
Version : 6.0 Sprint 6F.2B
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

import pandas as pd


@dataclass(slots=True)
class ValidationDataset:
    window_id: int
    symbol: str
    data: pd.DataFrame
    start: pd.Timestamp
    end: pd.Timestamp
    rows: int
    metadata: Dict[str, Any]

    def validate(self) -> None:
        if self.data is None or self.data.empty:
            raise ValueError("Validation dataset is empty.")

        if self.rows != len(self.data):
            raise ValueError("Validation row count mismatch.")

        if self.start > self.end:
            raise ValueError(
                "Validation start cannot be after validation end."
            )
