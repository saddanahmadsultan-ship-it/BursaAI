BursaAI v6.0 Professional Framework
Sprint 4B - Loader Adapter + Indicator Adapter

NEW FILES
---------
Adapters/stock_list_adapter.py
Adapters/loader_adapter.py
Adapters/indicator_adapter.py
Adapters/data_adapters.py
Tests/test_sprint4b.py
Tests/test_sprint4b_core_imports.py

UPDATED
-------
Adapters/__init__.py

LEGACY FUNCTIONS WRAPPED
------------------------
Core.stock_loader.load_stock_list
Core.data_loader.load_stock
Core.indicators.add_indicators

INSTALLATION
------------
Extract into the BursaAI project root.
Merge Adapters and Tests folders.

DO NOT modify:
- main.py
- Core/
- Framework/

TESTS
-----
From BursaAI root:

python -c "from Adapters.loader_adapter import LoaderAdapter; print('LOADER ADAPTER OK')"
python -c "from Adapters.indicator_adapter import IndicatorAdapter; print('INDICATOR ADAPTER OK')"
python -c "from Adapters.stock_list_adapter import StockListAdapter; print('STOCK LIST ADAPTER OK')"

python Tests/test_sprint4b.py
python Tests/test_sprint4b_core_imports.py

The main test uses fake data and does not require internet access.
The Core import test only imports real Core functions; it does not download data.
