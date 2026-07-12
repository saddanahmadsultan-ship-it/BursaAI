"""
=========================================================
BursaAI Historical DataFrame Validator
Version : 6.0 Sprint 6F.2A
=========================================================
"""

from __future__ import annotations

from typing import Iterable, List

import pandas as pd

from Framework.exceptions import ValidationError


class DataFrameValidator:
    REQUIRED_COLUMNS = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]

    def __init__(
        self,
        required_columns: Iterable[str] | None = None,
        minimum_rows: int = 50,
    ):
        self.required_columns = list(
            required_columns or self.REQUIRED_COLUMNS
        )
        self.minimum_rows = max(
            int(minimum_rows),
            1,
        )

    def validate(self, data: pd.DataFrame) -> None:
        if data is None:
            raise ValidationError(
                "Historical dataset is None."
            )

        if not isinstance(data, pd.DataFrame):
            raise ValidationError(
                "Historical dataset must be a pandas DataFrame."
            )

        if data.empty:
            raise ValidationError(
                "Historical dataset is empty."
            )

        if len(data) < self.minimum_rows:
            raise ValidationError(
                f"Historical dataset requires at least "
                f"{self.minimum_rows} rows."
            )

        missing = [
            column
            for column in self.required_columns
            if column not in data.columns
        ]

        if missing:
            raise ValidationError(
                "Missing required OHLCV columns: "
                + ", ".join(missing)
            )

        if not isinstance(
            data.index,
            pd.DatetimeIndex,
        ):
            raise ValidationError(
                "Historical dataset index must be DatetimeIndex."
            )

        if data.index.has_duplicates:
            raise ValidationError(
                "Historical dataset contains duplicate timestamps."
            )

        if not data.index.is_monotonic_increasing:
            raise ValidationError(
                "Historical dataset index must be sorted ascending."
            )

        numeric_columns: List[str] = [
            column
            for column in self.required_columns
            if column in data.columns
        ]

        for column in numeric_columns:
            if not pd.api.types.is_numeric_dtype(
                data[column]
            ):
                raise ValidationError(
                    f"Column {column} must be numeric."
                )

        invalid_price = (
            (data["High"] < data["Low"])
            | (data["Open"] < 0)
            | (data["High"] < 0)
            | (data["Low"] < 0)
            | (data["Close"] < 0)
            | (data["Volume"] < 0)
        )

        if invalid_price.any():
            raise ValidationError(
                "Historical dataset contains invalid OHLCV values."
            )
