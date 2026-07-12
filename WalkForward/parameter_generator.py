"""
=========================================================
BursaAI Parameter Generator
Version : 6.0 Sprint 6F.6A
=========================================================
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

from Framework.exceptions import ValidationError
from WalkForward.parameter_space import ParameterSpace


@dataclass(slots=True)
class GeneratedParameterSet:
    parameter_id: int
    parameters: Dict[str, Any]
    source: str = "GRID"


class ParameterGenerator:
    """
    Supports:
    - full grid generation
    - reproducible random sampling
    - unique parameter sets
    """

    def __init__(
        self,
        parameter_space: ParameterSpace,
        *,
        random_seed: Optional[int] = None,
    ):
        self.parameter_space = parameter_space
        self.random_seed = random_seed

    def generate_grid(
        self,
    ) -> List[GeneratedParameterSet]:
        combinations = (
            self.parameter_space.combinations()
        )

        return [
            GeneratedParameterSet(
                parameter_id=index,
                parameters=dict(parameters),
                source="GRID",
            )
            for index, parameters in enumerate(
                combinations,
                start=1,
            )
        ]

    def generate_random(
        self,
        count: int,
    ) -> List[GeneratedParameterSet]:
        count = int(count)

        if count <= 0:
            raise ValidationError(
                "Random parameter count must be positive."
            )

        combinations = (
            self.parameter_space.combinations()
        )

        if count > len(combinations):
            raise ValidationError(
                "Requested random sample exceeds available "
                "parameter combinations."
            )

        rng = random.Random(
            self.random_seed
        )

        selected = rng.sample(
            combinations,
            count,
        )

        return [
            GeneratedParameterSet(
                parameter_id=index,
                parameters=dict(parameters),
                source="RANDOM",
            )
            for index, parameters in enumerate(
                selected,
                start=1,
            )
        ]
