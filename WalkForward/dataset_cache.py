"""
=========================================================
BursaAI Historical Dataset Cache
Version : 6.0 Sprint 6F.2A
=========================================================
"""

from __future__ import annotations

from copy import deepcopy
from typing import Dict

import pandas as pd


class DatasetCache:
    def __init__(self):
        self._datasets: Dict[str, pd.DataFrame] = {}

    def set(
        self,
        key: str,
        data: pd.DataFrame,
    ) -> None:
        self._datasets[str(key)] = data.copy(
            deep=True
        )

    def get(
        self,
        key: str,
    ) -> pd.DataFrame | None:
        data = self._datasets.get(
            str(key)
        )

        if data is None:
            return None

        return data.copy(
            deep=True
        )

    def has(self, key: str) -> bool:
        return str(key) in self._datasets

    def delete(self, key: str) -> None:
        self._datasets.pop(
            str(key),
            None,
        )

    def clear(self) -> None:
        self._datasets.clear()

    def size(self) -> int:
        return len(self._datasets)
