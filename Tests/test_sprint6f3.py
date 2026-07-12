from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from Framework.infrastructure import build_infrastructure
from WalkForward.dataset_splitter import DatasetSplitter
from WalkForward.training_report import TrainingReport
from WalkForward.training_services import register_training_runner


def build_data():
    dates = pd.bdate_range('2022-01-03', '2024-12-31')
    values = [10 + i * 0.01 for i in range(len(dates))]
    return pd.DataFrame({
        'Open': values,
        'High': [v + 0.2 for v in values],
        'Low': [v - 0.2 for v in values],
        'Close': [v + 0.1 for v in values],
        'Volume': [1000 + i for i in range(len(dates))],
    }, index=dates)


def build_splits():
    data = build_data()
    windows = [
        {'window_id': 1, 'training_start': '2022-01-03', 'training_end': '2022-12-30', 'validation_start': '2023-01-02', 'validation_end': '2023-03-31'},
        {'window_id': 2, 'training_start': '2022-04-01', 'training_end': '2023-03-31', 'validation_start': '2023-04-03', 'validation_end': '2023-06-30'},
        {'window_id': 3, 'training_start': '2022-07-01', 'training_end': '2023-06-30', 'validation_start': '2023-07-03', 'validation_end': '2023-09-29'},
    ]
    splitter = DatasetSplitter(minimum_training_rows=200, minimum_validation_rows=50)
    return splitter.split_many('1155.KL', data, windows)


def fake_trainer(data, split, context):
    return {
        'parameters': {'short_window': 20 + split.window_id, 'long_window': 50 + split.window_id},
        'metrics': {'training_score': 70 + split.window_id, 'rows': len(data)},
        'artifacts': {'model_name': f'model_window_{split.window_id}'},
        'warnings': [],
    }


def main():
    infrastructure = build_infrastructure()
    events = []
    infrastructure.events.subscribe('TrainingWindowCompleted', lambda event: events.append(event.name))
    infrastructure.events.subscribe('TrainingRunCompleted', lambda event: events.append(event.name))

    runner = register_training_runner(
        infrastructure.services,
        trainer=fake_trainer,
        trainer_name='moving_average',
    )

    result = runner.run_many(build_splits(), context={'strategy': 'moving_average'})

    assert result.total_windows == 3
    assert result.successful_windows == 3
    assert result.failed_windows == 0
    assert result.success is True
    assert result.results[0].parameters['short_window'] == 21
    assert result.results[0].metrics['training_score'] == 71.0
    assert result.results[0].artifacts['model_name'] == 'model_window_1'
    assert events.count('TrainingWindowCompleted') == 3
    assert events.count('TrainingRunCompleted') == 1
    assert infrastructure.services.resolve('training_registry').names() == ['moving_average']
    assert infrastructure.services.resolve('training_window_runner') is runner

    rendered = TrainingReport(result=result).render_text()
    assert 'BURSAAI TRAINING WINDOW REPORT' in rendered
    assert 'Total Windows       : 3' in rendered

    print('=' * 90)
    print('BURSAAI v6.0 SPRINT 6F.3 TEST')
    print('=' * 90)
    print('Training Window Model    : OK')
    print('Training Run Model       : OK')
    print('Training Registry        : OK')
    print('Single Window Runner     : OK')
    print('Multiple Window Runner   : OK')
    print('Parameter Capture        : OK')
    print('Metric Capture           : OK')
    print('Artifact Capture         : OK')
    print('Training Events          : OK')
    print('Service Registration     : OK')
    print('Training Report          : OK')
    print('=' * 90)
    print('SPRINT 6F.3 TRAINING WINDOW RUNNER OK')


if __name__ == '__main__':
    main()
