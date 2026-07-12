"""
BursaAI v6.0 Sprint 4B validation test.

This test does not download market data.
It uses injected fake legacy functions.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


import pandas as pd

from Adapters.data_adapters import register_data_adapters
from Adapters.stock_list_adapter import StockListAdapter
from Framework.context import AnalysisContext
from Framework.engine_registry import EngineRegistry
from Framework.logger import FrameworkLogger
from Framework.pipeline import Pipeline
from Framework.pipeline_policy import PipelinePolicy


def fake_stock_list():
    return [
        "1155.KL",
        "1023.KL",
        "1295.KL",
    ]


def fake_load_stock(symbol):
    assert symbol == "1155.KL"

    return pd.DataFrame(
        {
            "Open": [10.0, 10.1, 10.2],
            "High": [10.2, 10.3, 10.4],
            "Low": [9.9, 10.0, 10.1],
            "Close": [10.1, 10.2, 10.3],
            "Volume": [1000, 1200, 1400],
        }
    )


def fake_add_indicators(data):
    enriched = data.copy()

    enriched["EMA20"] = enriched["Close"].rolling(
        2,
        min_periods=1,
    ).mean()

    enriched["RSI"] = [
        50.0,
        55.0,
        60.0,
    ]

    return enriched


def test_stock_list_adapter():
    adapter = StockListAdapter(
        loader=fake_stock_list
    )

    context = AnalysisContext(
        symbol="SYSTEM"
    )

    result = adapter.execute(context)

    assert result.success is True

    assert context.metadata["stock_list"] == [
        "1155.KL",
        "1023.KL",
        "1295.KL",
    ]


def test_loader_indicator_pipeline():
    logger = FrameworkLogger(
        echo=False
    )

    registry = EngineRegistry(
        logger=logger
    )

    register_data_adapters(
        registry,
        data_loader=fake_load_stock,
        indicator_function=fake_add_indicators,
        minimum_rows=3,
        required_indicator_columns=[
            "EMA20",
            "RSI",
        ],
    )

    pipeline = Pipeline(
        name="Sprint 4B Data Pipeline",
        registry=registry,
        policy=PipelinePolicy(
            failure_mode="stop",
            validate_dependencies=True,
            record_context_snapshot=True,
        ),
        logger=logger,
    )

    context = AnalysisContext(
        symbol="1155.KL"
    )

    report = pipeline.execute(context)

    assert report.success is True
    assert report.successful_engines == 2
    assert report.failed_engines == 0
    assert report.skipped_engines == 0

    assert context.data is not None
    assert context.indicators is not None

    assert len(context.data) == 3
    assert "EMA20" in context.data.columns
    assert "RSI" in context.data.columns

    assert context.metadata["data_loaded"] is True
    assert context.metadata["data_rows"] == 3
    assert context.metadata["indicators_added"] is True
    assert context.metadata["indicator_rows"] == 3

    assert registry.names() == [
        "Loader Adapter",
        "Indicator Adapter",
    ]


def test_minimum_row_validation():
    registry = EngineRegistry(
        logger=FrameworkLogger(
            echo=False
        )
    )

    register_data_adapters(
        registry,
        data_loader=fake_load_stock,
        indicator_function=fake_add_indicators,
        minimum_rows=10,
    )

    pipeline = Pipeline(
        name="Minimum Row Test",
        registry=registry,
        policy=PipelinePolicy(
            failure_mode="stop",
        ),
    )

    report = pipeline.execute(
        AnalysisContext(
            symbol="1155.KL"
        )
    )

    assert report.success is False
    assert report.failed_engines == 1
    assert report.stopped_early is True


def main():
    test_stock_list_adapter()
    test_loader_indicator_pipeline()
    test_minimum_row_validation()

    print("=" * 74)
    print("BURSAAI v6.0 SPRINT 4B TEST")
    print("=" * 74)
    print("Stock List Adapter      : OK")
    print("Loader Adapter          : OK")
    print("Indicator Adapter       : OK")
    print("Adapter Registration    : OK")
    print("Pipeline Integration    : OK")
    print("Data Context Storage    : OK")
    print("Indicator Context Sync  : OK")
    print("Minimum Row Validation  : OK")
    print("Required Column Check   : OK")
    print("=" * 74)
    print("SPRINT 4B DATA ADAPTER FOUNDATION OK")


if __name__ == "__main__":
    main()
