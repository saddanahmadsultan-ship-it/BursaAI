from __future__ import annotations
from typing import Callable, Dict, List
from Framework.exceptions import ConfigurationError

class TrainingRegistry:
    def __init__(self):
        self._trainers: Dict[str, Callable] = {}

    def register(self, name: str, trainer: Callable, *, replace: bool = False) -> None:
        key = str(name).strip().lower()
        if not key:
            raise ConfigurationError('Trainer name cannot be empty.')
        if not callable(trainer):
            raise ConfigurationError('Trainer must be callable.')
        if key in self._trainers and not replace:
            raise ConfigurationError(f'Trainer already registered: {key}')
        self._trainers[key] = trainer

    def get(self, name: str) -> Callable:
        key = str(name).strip().lower()
        if key not in self._trainers:
            raise ConfigurationError(f'Trainer not found: {key}')
        return self._trainers[key]

    def names(self) -> List[str]:
        return sorted(self._trainers)
