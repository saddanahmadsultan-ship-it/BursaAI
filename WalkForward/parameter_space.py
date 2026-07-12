"""
=========================================================
BursaAI Parameter Space
Version : 6.0 Sprint 6F.6A
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
from typing import Any, Callable, Dict, Iterable, List, Optional

from Framework.exceptions import ValidationError


@dataclass(slots=True)
class ParameterDefinition:
    name: str
    values: List[Any]
    description: str = ""
    validator: Optional[Callable[[Any], bool]] = None

    def validate(self) -> None:
        if not str(self.name).strip():
            raise ValidationError(
                "Parameter name cannot be empty."
            )

        if not self.values:
            raise ValidationError(
                f"Parameter {self.name} requires at least one value."
            )

        if self.validator is not None:
            invalid = [
                value
                for value in self.values
                if not self.validator(value)
            ]

            if invalid:
                raise ValidationError(
                    f"Parameter {self.name} contains invalid values: "
                    f"{invalid}"
                )


@dataclass(slots=True)
class ParameterSpace:
    parameters: Dict[str, ParameterDefinition] = field(
        default_factory=dict
    )
    constraints: List[
        Callable[[Dict[str, Any]], bool]
    ] = field(default_factory=list)

    def add(
        self,
        name: str,
        values: Iterable[Any],
        *,
        description: str = "",
        validator: Optional[Callable[[Any], bool]] = None,
    ) -> None:
        definition = ParameterDefinition(
            name=str(name),
            values=list(values),
            description=str(description),
            validator=validator,
        )

        definition.validate()

        self.parameters[
            definition.name
        ] = definition

    def add_constraint(
        self,
        constraint: Callable[
            [Dict[str, Any]],
            bool,
        ],
    ) -> None:
        if not callable(constraint):
            raise ValidationError(
                "Parameter constraint must be callable."
            )

        self.constraints.append(
            constraint
        )

    def names(self) -> List[str]:
        return list(
            self.parameters.keys()
        )

    def validate(self) -> None:
        if not self.parameters:
            raise ValidationError(
                "Parameter space cannot be empty."
            )

        for definition in self.parameters.values():
            definition.validate()

    def is_valid(
        self,
        parameters: Dict[str, Any],
    ) -> bool:
        return all(
            constraint(parameters)
            for constraint in self.constraints
        )

    def combinations(self) -> List[Dict[str, Any]]:
        self.validate()

        names = self.names()

        values = [
            self.parameters[name].values
            for name in names
        ]

        output = []

        for combination in product(*values):
            parameters = dict(
                zip(
                    names,
                    combination,
                )
            )

            if self.is_valid(parameters):
                output.append(parameters)

        return output

    def size(self) -> int:
        return len(
            self.combinations()
        )
