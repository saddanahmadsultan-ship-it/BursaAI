"""
=========================================================
BursaAI Historical Dataset Builder
Version : 6.0 Sprint 6F.2A
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Optional

import pandas as pd

from WalkForward.dataframe_validator import DataFrameValidator
from WalkForward.dataset_cache import DatasetCache
from WalkForward.history_loader import HistoricalDataLoader


@dataclass(slots=True)
class HistoricalDataset:
    symbol: str
    data: pd.DataFrame
    missing_intervals: list[str] = field(
        default_factory=list
    )
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


class HistoricalDatasetBuilder:
    COLUMN_ALIASES = {
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "adj close": "Adj Close",
        "adj_close": "Adj Close",
        "volume": "Volume",
    }

    def __init__(
        self,
        loader: HistoricalDataLoader,
        validator: Optional[
            DataFrameValidator
        ] = None,
        cache: Optional[
            DatasetCache
        ] = None,
        expected_frequency: str = "B",
    ):
        self.loader = loader
        self.validator = (
            validator
            or DataFrameValidator()
        )
        self.cache = (
            cache
            or DatasetCache()
        )
        self.expected_frequency = str(
            expected_frequency
        )

    def _normalise_columns(
        self,
        data: pd.DataFrame,
    ) -> pd.DataFrame:
        rename_map = {}

        for column in data.columns:
            text = str(column).strip()
            key = text.lower()

            if key in self.COLUMN_ALIASES:
                rename_map[column] = (
                    self.COLUMN_ALIASES[key]
                )
            else:
                rename_map[column] = text

        return data.rename(
            columns=rename_map
        )

    def _normalise_index(
        self,
        data: pd.DataFrame,
    ) -> pd.DataFrame:
        output = data.copy()

        if not isinstance(
            output.index,
            pd.DatetimeIndex,
        ):
            candidate = None

            for name in (
                "Date",
                "Datetime",
                "Timestamp",
                "date",
                "datetime",
                "timestamp",
            ):
                if name in output.columns:
                    candidate = name
                    break

            if candidate is None:
                output.index = pd.to_datetime(
                    output.index,
                    errors="coerce",
                )
            else:
                output.index = pd.to_datetime(
                    output.pop(candidate),
                    errors="coerce",
                )

        output = output[
            ~output.index.isna()
        ]

        if output.index.tz is not None:
            output.index = output.index.tz_convert(
                None
            )

        output = output[
            ~output.index.duplicated(
                keep="last"
            )
        ]

        output = output.sort_index()

        return output

    def _normalise_numeric(
        self,
        data: pd.DataFrame,
    ) -> pd.DataFrame:
        output = data.copy()

        for column in (
            "Open",
            "High",
            "Low",
            "Close",
            "Adj Close",
            "Volume",
        ):
            if column in output.columns:
                output[column] = pd.to_numeric(
                    output[column],
                    errors="coerce",
                )

        required = [
            column
            for column in self.validator.required_columns
            if column in output.columns
        ]

        output = output.dropna(
            subset=required
        )

        return output

    def _detect_missing_intervals(
        self,
        data: pd.DataFrame,
    ) -> list[str]:
        if data.empty:
            return []

        expected = pd.date_range(
            start=data.index.min(),
            end=data.index.max(),
            freq=self.expected_frequency,
        )

        missing = expected.difference(
            data.index
        )

        return [
            timestamp.isoformat()
            for timestamp in missing
        ]

    def build(
        self,
        symbol: str,
        *,
        use_cache: bool = True,
    ) -> HistoricalDataset:
        cache_key = f"{symbol}:{self.expected_frequency}"

        if use_cache:
            cached = self.cache.get(
                cache_key
            )

            if cached is not None:
                return HistoricalDataset(
                    symbol=symbol,
                    data=cached,
                    missing_intervals=(
                        self._detect_missing_intervals(
                            cached
                        )
                    ),
                    metadata={
                        "source": "cache",
                        "rows": len(cached),
                    },
                )

        data = self.loader.load(symbol)
        data = self._normalise_columns(data)
        data = self._normalise_index(data)
        data = self._normalise_numeric(data)

        self.validator.validate(data)

        missing = self._detect_missing_intervals(
            data
        )

        self.cache.set(
            cache_key,
            data,
        )

        return HistoricalDataset(
            symbol=symbol,
            data=data,
            missing_intervals=missing,
            metadata={
                "source": "loader",
                "rows": len(data),
                "start": data.index.min().isoformat(),
                "end": data.index.max().isoformat(),
                "missing_intervals": len(missing),
            },
        )
