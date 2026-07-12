"""
=========================================================
BursaAI Data Adapter Registration
Version : 6.0 Sprint 4B
=========================================================
"""

from __future__ import annotations

from typing import Callable, Iterable, Optional

from Adapters.indicator_adapter import IndicatorAdapter
from Adapters.loader_adapter import LoaderAdapter
from Adapters.stock_list_adapter import StockListAdapter
from Framework.engine_registry import EngineRegistry


def register_data_adapters(
    registry: EngineRegistry,
    *,
    stock_list_loader: Optional[Callable[[], Iterable[str]]] = None,
    data_loader: Optional[Callable[[str], object]] = None,
    indicator_function: Optional[Callable[[object], object]] = None,
    minimum_rows: int = 1,
    required_indicator_columns: Optional[Iterable[str]] = None,
    include_stock_list: bool = False,
) -> EngineRegistry:
    """
    Register Sprint 4B adapters using injectable legacy functions.
    """

    if include_stock_list:
        registry.register(
            StockListAdapter(
                loader=stock_list_loader,
            )
        )

    registry.register(
        LoaderAdapter(
            loader=data_loader,
            minimum_rows=minimum_rows,
        )
    )

    registry.register(
        IndicatorAdapter(
            indicator_function=indicator_function,
            required_columns=required_indicator_columns,
        )
    )

    return registry
