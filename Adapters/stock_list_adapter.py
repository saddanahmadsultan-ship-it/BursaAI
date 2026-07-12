"""
=========================================================
BursaAI Stock List Adapter
Version : 6.0 Sprint 4B
=========================================================
"""

from __future__ import annotations

from typing import Callable, Iterable, List, Optional

from Adapters.base_adapter import BaseAdapter
from Framework.context import AnalysisContext
from Framework.exceptions import DataError
from Framework.metadata import EngineMetadata


class StockListAdapter(BaseAdapter):
    """
    Wrap Core.stock_loader.load_stock_list().

    The adapter stores the resulting list in:
        context.metadata["stock_list"]
    """

    METADATA = EngineMetadata(
        name="Stock List Adapter",
        version="6.0",
        priority=5,
        category="data",
    )

    def __init__(
        self,
        loader: Optional[Callable[[], Iterable[str]]] = None,
    ):
        super().__init__(metadata=self.METADATA)

        if loader is None:
            from Core.stock_loader import load_stock_list
            loader = load_stock_list

        self.loader = loader

    def run_legacy(self, context: AnalysisContext):
        stocks = self.loader()

        if stocks is None:
            raise DataError("Stock list loader returned None.")

        normalized: List[str] = []

        for symbol in stocks:
            value = str(symbol).strip()

            if value:
                normalized.append(value)

        if not normalized:
            raise DataError("Stock list is empty.")

        return normalized

    def sync_to_context(self, context, legacy_output) -> None:
        context.metadata["stock_list"] = list(
            legacy_output
        )
