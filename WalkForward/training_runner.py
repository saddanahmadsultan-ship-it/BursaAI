from __future__ import annotations
from time import perf_counter
from typing import Any, Callable, Dict, Iterable, Optional
from Framework.event_bus import EventBus
from Framework.exceptions import ValidationError
from Framework.service_container import ServiceContainer
from WalkForward.dataset_splitter import DatasetSplit
from WalkForward.training_models import TrainingRunResult, TrainingWindowResult

class TrainingWindowRunner:
    def __init__(self, trainer: Callable[..., Dict[str, Any]], *, services: Optional[ServiceContainer] = None, event_bus: Optional[EventBus] = None, stop_on_error: bool = False):
        if not callable(trainer):
            raise ValidationError('TrainingWindowRunner requires a callable trainer.')
        self.trainer = trainer
        self.services = services
        self.stop_on_error = bool(stop_on_error)
        if event_bus is not None:
            self.event_bus = event_bus
        elif services is not None and services.contains('event_bus'):
            self.event_bus = services.resolve('event_bus')
        else:
            self.event_bus = None

    def _call_trainer(self, split: DatasetSplit, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        data = split.training.data
        try:
            output = self.trainer(data, split, context)
        except TypeError:
            try:
                output = self.trainer(data, split)
            except TypeError:
                output = self.trainer(data)
        if output is None:
            output = {}
        if not isinstance(output, dict):
            raise ValidationError('Trainer output must be a dictionary.')
        return output

    def run_one(self, split: DatasetSplit, *, context: Optional[Dict[str, Any]] = None) -> TrainingWindowResult:
        split.validate()
        started = perf_counter()
        try:
            output = self._call_trainer(split, context)
            result = TrainingWindowResult(
                window_id=split.window_id,
                symbol=split.training.symbol,
                success=True,
                parameters=dict(output.get('parameters', {})),
                metrics={str(k): float(v) for k, v in dict(output.get('metrics', {})).items()},
                artifacts=dict(output.get('artifacts', {})),
                warnings=[str(v) for v in output.get('warnings', [])],
                duration_ms=(perf_counter() - started) * 1000,
            )
        except Exception as error:
            result = TrainingWindowResult(
                window_id=split.window_id,
                symbol=split.training.symbol,
                success=False,
                errors=[f'{type(error).__name__}: {error}'],
                duration_ms=(perf_counter() - started) * 1000,
            )
            if self.stop_on_error:
                raise
        if self.event_bus is not None:
            self.event_bus.publish('TrainingWindowCompleted', payload={
                'window_id': result.window_id,
                'symbol': result.symbol,
                'success': result.success,
                'parameters': dict(result.parameters),
                'metrics': dict(result.metrics),
                'warnings': list(result.warnings),
                'errors': list(result.errors),
                'duration_ms': result.duration_ms,
            }, source='Training Window Runner')
        return result

    def run_many(self, splits: Iterable[DatasetSplit], *, context: Optional[Dict[str, Any]] = None) -> TrainingRunResult:
        items = list(splits)
        if not items:
            raise ValidationError('Training runner requires at least one dataset split.')
        started = perf_counter()
        results = [self.run_one(split, context=context) for split in items]
        successful = sum(1 for result in results if result.success)
        run_result = TrainingRunResult(
            symbol=items[0].training.symbol,
            total_windows=len(results),
            successful_windows=successful,
            failed_windows=len(results) - successful,
            results=results,
            duration_ms=(perf_counter() - started) * 1000,
        )
        if self.event_bus is not None:
            self.event_bus.publish('TrainingRunCompleted', payload=run_result.to_dict(), source='Training Window Runner')
        return run_result
