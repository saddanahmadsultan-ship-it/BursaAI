"""
Sprint 4B import-only smoke test for real Core modules.

This test does not call Yahoo Finance or download data.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main():
    from Core.stock_loader import load_stock_list
    from Core.data_loader import load_stock
    from Core.indicators import add_indicators

    from Adapters.stock_list_adapter import StockListAdapter
    from Adapters.loader_adapter import LoaderAdapter
    from Adapters.indicator_adapter import IndicatorAdapter

    assert callable(load_stock_list)
    assert callable(load_stock)
    assert callable(add_indicators)

    StockListAdapter(loader=load_stock_list)
    LoaderAdapter(loader=load_stock)
    IndicatorAdapter(
        indicator_function=add_indicators
    )

    print("=" * 74)
    print("BURSAAI v6.0 SPRINT 4B CORE IMPORT TEST")
    print("=" * 74)
    print("Core.stock_loader       : OK")
    print("Core.data_loader        : OK")
    print("Core.indicators         : OK")
    print("Stock List Adapter      : OK")
    print("Loader Adapter          : OK")
    print("Indicator Adapter       : OK")
    print("=" * 74)
    print("SPRINT 4B CORE IMPORTS OK")


if __name__ == "__main__":
    main()
