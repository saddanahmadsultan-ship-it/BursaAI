"""
=========================================================
BursaAI Data Loader Adapter
Version : 6.0 Sprint 4B
=========================================================
"""

from __future__ import annotations

from typing import Callable, Optional

from Adapters.base_adapter import BaseAdapter
from Framework.context import AnalysisContext
from Framework.exceptions import DataError
from Framework.metadata import EngineMetadata


class LoaderAdapter(BaseAdapter):
    """
    Wrap Core.data_loader.load_stock(symbol).

    Output:
        context.data
    """

    METADATA = EngineMetadata(
        name="Loader Adapter",
        version="6.0",
        priority=10,
        category="data",
    )

    def __init__(
        self,
        loader: Optional[Callable[[str], object]] = None,
        minimum_rows: int = 1,
    ):
        super().__init__(metadata=self.METADATA)

        if loader is None:
            from Core.data_loader import load_stock
            loader = load_stock

        self.loader = loader
        self.minimum_rows = max(int(minimum_rows), 1)

    def run_legacy(self, context: AnalysisContext):
        data = self.loader(context.symbol)

        if data is None:
            raise DataError(
                f"No market data returned for {context.symbol}."
            )

        if getattr(data, "empty", False):
            raise DataError(
                f"Market data is empty for {context.symbol}."
            )

        try:
            row_count = len(data)
        except TypeError as error:
            raise DataError(
                "Market data must support len()."
            ) from error

        if row_count < self.minimum_rows:
            raise DataError(
                f"Insufficient rows for {context.symbol}: "
                f"{row_count} < {self.minimum_rows}."
            )

        return data

    def sync_to_context(self, context, legacy_output) -> None:
        context.data = legacy_output

        context.metadata["data_loaded"] = True
        context.metadata["data_rows"] = len(
            legacy_output
        )

        columns = getattr(
            legacy_output,
            "columns",
            [],
        )

        context.metadata["data_columns"] = [
            str(column)
            for column in columns
        ]
