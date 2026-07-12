from __future__ import annotations
from typing import Callable
from Framework.service_container import ServiceContainer
from WalkForward.training_registry import TrainingRegistry
from WalkForward.training_runner import TrainingWindowRunner

def register_training_runner(services: ServiceContainer, *, trainer: Callable, trainer_name: str = 'default', stop_on_error: bool = False) -> TrainingWindowRunner:
    if services.contains('training_registry'):
        registry = services.resolve('training_registry')
    else:
        registry = TrainingRegistry()
        services.register_instance('training_registry', registry, replace=True)
    registry.register(trainer_name, trainer, replace=True)
    runner = TrainingWindowRunner(trainer=trainer, services=services, stop_on_error=stop_on_error)
    services.register_instance('training_window_runner', runner, replace=True)
    return runner
