"""
=========================================================
BursaAI Historical Data Loader
Version : 6.0 Sprint 6F.2A
=========================================================
"""

from __future__ import annotations

from typing import Callable, Optional

import pandas as pd

from Framework.exceptions import DataError


class HistoricalDataLoader:
    """
    Wraps Core.data_loader.load_stock(symbol) or an injected loader.
    """

    def __init__(
        self,
        loader: Optional[
            Callable[[str], pd.DataFrame]
        ] = None,
    ):
        if loader is None:
            from Core.data_loader import load_stock
            loader = load_stock

        self.loader = loader

    def load(self, symbol: str) -> pd.DataFrame:
        symbol = str(symbol).strip()

        if not symbol:
            raise DataError(
                "HistoricalDataLoader requires a symbol."
            )

        data = self.loader(symbol)

        if data is None:
            raise DataError(
                f"No historical data returned for {symbol}."
            )

        if not isinstance(data, pd.DataFrame):
            raise DataError(
                "Historical loader must return a pandas DataFrame."
            )

        return data.copy()
