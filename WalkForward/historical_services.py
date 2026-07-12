from __future__ import annotations
from typing import Any, Optional
from Framework.exceptions import ConfigurationError
from Framework.service_container import ServiceContainer
from WalkForward.historical_engine import HistoricalEngine
from WalkForward.split_validator import SplitValidator

def register_historical_engine(services: ServiceContainer, *, window_generator: Optional[Any]=None, replace: bool=True) -> HistoricalEngine:
    dataset_builder=services.resolve('historical_dataset_builder')
    dataset_splitter=services.resolve('dataset_splitter')
    validator=services.resolve('dataset_split_validator') if services.contains('dataset_split_validator') else SplitValidator()
    if window_generator is None:
        if services.contains('walkforward_window_generator'):
            window_generator=services.resolve('walkforward_window_generator')
        elif services.contains('window_generator'):
            window_generator=services.resolve('window_generator')
        else:
            raise ConfigurationError('No walk-forward window generator is registered.')
    engine=HistoricalEngine(dataset_builder,window_generator,dataset_splitter,validator)
    services.register_instance('historical_engine',engine,replace=replace)
    return engine
