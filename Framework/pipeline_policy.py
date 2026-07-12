"""
=========================================================
BursaAI Pipeline Policy
Version : 6.0 Sprint 3
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

FailureMode = Literal[
    "continue",
    "stop",
    "skip_dependents",
]


@dataclass(slots=True)
class PipelinePolicy:
    """
    Controls how the pipeline reacts to errors and skipped engines.
    """

    failure_mode: FailureMode = "continue"
    validate_dependencies: bool = True
    stop_on_context_error: bool = False
    allow_disabled_engines: bool = True
    record_context_snapshot: bool = False

    def validate(self) -> None:
        valid_modes = {
            "continue",
            "stop",
            "skip_dependents",
        }

        if self.failure_mode not in valid_modes:
            raise ValueError(
                "Invalid failure_mode. "
                f"Expected one of {sorted(valid_modes)}."
            )
