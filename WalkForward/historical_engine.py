from __future__ import annotations
from typing import Any, Optional
from Framework.exceptions import ValidationError
from WalkForward.dataset_builder import HistoricalDatasetBuilder
from WalkForward.dataset_splitter import DatasetSplitter
from WalkForward.historical_models import HistoricalRunResult
from WalkForward.split_validator import SplitValidator

class HistoricalEngine:
    def __init__(self, dataset_builder: HistoricalDatasetBuilder, window_generator: Any, dataset_splitter: DatasetSplitter, split_validator: Optional[SplitValidator]=None):
        self.dataset_builder=dataset_builder
        self.window_generator=window_generator
        self.dataset_splitter=dataset_splitter
        self.split_validator=split_validator or SplitValidator()

    def _generate_windows(self, data, symbol: str, config: Any=None) -> list:
        generator=self.window_generator
        if hasattr(generator,'generate'):
            try: windows=generator.generate(data=data,symbol=symbol,config=config)
            except TypeError:
                try: windows=generator.generate(data,config)
                except TypeError: windows=generator.generate(data)
        elif callable(generator):
            try: windows=generator(data=data,symbol=symbol,config=config)
            except TypeError:
                try: windows=generator(data,config)
                except TypeError: windows=generator(data)
        else:
            raise ValidationError('Window generator must be callable or expose generate().')
        items=list(windows or [])
        if not items:
            raise ValidationError(f'No walk-forward windows generated for {symbol}.')
        return items

    def run(self, symbol: str, *, config: Any=None, use_cache: bool=True, skip_invalid_windows: bool=False) -> HistoricalRunResult:
        dataset=self.dataset_builder.build(symbol,use_cache=use_cache)
        windows=self._generate_windows(dataset.data,symbol,config)
        splits=self.dataset_splitter.split_many(symbol=symbol,data=dataset.data,windows=windows,skip_invalid=skip_invalid_windows)
        self.split_validator.validate(splits)
        warnings=[]
        if dataset.missing_intervals:
            warnings.append(f'{len(dataset.missing_intervals)} missing intervals detected.')
        return HistoricalRunResult(
            symbol=symbol,
            windows_generated=len(windows),
            splits_created=len(splits),
            splits=splits,
            warnings=warnings,
            metadata={
                'dataset_rows':len(dataset.data),
                'dataset_source':dataset.metadata.get('source','unknown'),
                'dataset_start':dataset.data.index.min().isoformat(),
                'dataset_end':dataset.data.index.max().isoformat(),
                'missing_intervals':len(dataset.missing_intervals),
            },
        )
