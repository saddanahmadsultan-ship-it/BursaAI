"""
=========================================================
BursaAI Dataset Splitter
Version : 6.0 Sprint 6F.2B
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

import pandas as pd

from Framework.exceptions import ValidationError
from WalkForward.training_dataset import TrainingDataset
from WalkForward.validation_dataset import ValidationDataset


@dataclass(slots=True)
class DatasetSplit:
    window_id: int
    training: TrainingDataset
    validation: ValidationDataset

    def validate(self) -> None:
        self.training.validate()
        self.validation.validate()

        if self.training.end >= self.validation.start:
            raise ValidationError(
                "Look-ahead leakage detected: training overlaps validation."
            )


class DatasetSplitter:
    """
    Split historical data using date windows.

    Window objects may be dictionaries or objects exposing:
        window_id
        training_start
        training_end
        validation_start
        validation_end
    """

    def __init__(
        self,
        minimum_training_rows: int = 50,
        minimum_validation_rows: int = 10,
        copy_data: bool = True,
    ):
        self.minimum_training_rows = max(
            int(minimum_training_rows),
            1,
        )
        self.minimum_validation_rows = max(
            int(minimum_validation_rows),
            1,
        )
        self.copy_data = bool(copy_data)

    def _value(self, window, name):
        if isinstance(window, dict):
            return window.get(name)

        return getattr(window, name)

    def _slice(
        self,
        data: pd.DataFrame,
        start,
        end,
    ) -> pd.DataFrame:
        start = pd.Timestamp(start)
        end = pd.Timestamp(end)

        output = data.loc[
            (data.index >= start)
            & (data.index <= end)
        ]

        return (
            output.copy(deep=True)
            if self.copy_data
            else output
        )

    def split_one(
        self,
        symbol: str,
        data: pd.DataFrame,
        window,
    ) -> DatasetSplit:
        if data is None or data.empty:
            raise ValidationError(
                "DatasetSplitter requires non-empty data."
            )

        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValidationError(
                "Dataset index must be DatetimeIndex."
            )

        window_id = int(
            self._value(window, "window_id")
        )

        training_start = pd.Timestamp(
            self._value(window, "training_start")
        )
        training_end = pd.Timestamp(
            self._value(window, "training_end")
        )
        validation_start = pd.Timestamp(
            self._value(window, "validation_start")
        )
        validation_end = pd.Timestamp(
            self._value(window, "validation_end")
        )

        if training_end >= validation_start:
            raise ValidationError(
                "Training window must end before validation starts."
            )

        training_data = self._slice(
            data,
            training_start,
            training_end,
        )

        validation_data = self._slice(
            data,
            validation_start,
            validation_end,
        )

        if len(training_data) < self.minimum_training_rows:
            raise ValidationError(
                f"Window {window_id} has insufficient training rows: "
                f"{len(training_data)} < {self.minimum_training_rows}."
            )

        if len(validation_data) < self.minimum_validation_rows:
            raise ValidationError(
                f"Window {window_id} has insufficient validation rows: "
                f"{len(validation_data)} < {self.minimum_validation_rows}."
            )

        training = TrainingDataset(
            window_id=window_id,
            symbol=str(symbol),
            data=training_data,
            start=training_data.index.min(),
            end=training_data.index.max(),
            rows=len(training_data),
            metadata={
                "requested_start": training_start.isoformat(),
                "requested_end": training_end.isoformat(),
            },
        )

        validation = ValidationDataset(
            window_id=window_id,
            symbol=str(symbol),
            data=validation_data,
            start=validation_data.index.min(),
            end=validation_data.index.max(),
            rows=len(validation_data),
            metadata={
                "requested_start": validation_start.isoformat(),
                "requested_end": validation_end.isoformat(),
            },
        )

        result = DatasetSplit(
            window_id=window_id,
            training=training,
            validation=validation,
        )

        result.validate()

        return result

    def split_many(
        self,
        symbol: str,
        data: pd.DataFrame,
        windows: Iterable,
        *,
        skip_invalid: bool = False,
    ) -> List[DatasetSplit]:
        output: List[DatasetSplit] = []

        for window in windows:
            try:
                output.append(
                    self.split_one(
                        symbol,
                        data,
                        window,
                    )
                )
            except Exception:
                if not skip_invalid:
                    raise

        return output
