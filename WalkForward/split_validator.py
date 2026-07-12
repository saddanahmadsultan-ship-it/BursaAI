"""
=========================================================
BursaAI Dataset Split Validator
Version : 6.0 Sprint 6F.2B
=========================================================
"""

from __future__ import annotations

from typing import Iterable

from Framework.exceptions import ValidationError
from WalkForward.dataset_splitter import DatasetSplit


class SplitValidator:
    def validate(
        self,
        splits: Iterable[DatasetSplit],
    ) -> None:
        items = list(splits)

        if not items:
            raise ValidationError(
                "No dataset splits were generated."
            )

        previous_validation_end = None
        seen_window_ids = set()

        for split in items:
            split.validate()

            if split.window_id in seen_window_ids:
                raise ValidationError(
                    f"Duplicate window id: {split.window_id}"
                )

            seen_window_ids.add(
                split.window_id
            )

            if (
                previous_validation_end is not None
                and split.validation.start
                <= previous_validation_end
            ):
                raise ValidationError(
                    "Validation windows overlap or are not ordered."
                )

            previous_validation_end = (
                split.validation.end
            )
