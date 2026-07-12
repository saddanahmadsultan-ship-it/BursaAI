from pathlib import Path
import sys
PROJECT_ROOT=Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path: sys.path.insert(0,str(PROJECT_ROOT))
import pandas as pd
from Framework.infrastructure import build_infrastructure
from WalkForward.dataset_services import register_historical_dataset_builder
from WalkForward.dataset_split_services import register_dataset_splitter
from WalkForward.historical_services import register_historical_engine
from WalkForward.historical_report import HistoricalReport

def fake_loader(symbol):
    dates=pd.bdate_range('2022-01-03','2025-12-31')
    return pd.DataFrame({'Open':10.0,'High':10.5,'Low':9.5,'Close':10.2,'Volume':1000},index=dates)

class FakeWindowGenerator:
    def generate(self,data,symbol=None,config=None):
        return [
            {'window_id':1,'training_start':'2022-01-03','training_end':'2022-12-30','validation_start':'2023-01-02','validation_end':'2023-03-31'},
            {'window_id':2,'training_start':'2022-04-01','training_end':'2023-03-31','validation_start':'2023-04-03','validation_end':'2023-06-30'},
            {'window_id':3,'training_start':'2022-07-01','training_end':'2023-06-30','validation_start':'2023-07-03','validation_end':'2023-09-29'},
        ]

def main():
    infrastructure=build_infrastructure()
    register_historical_dataset_builder(infrastructure.services,loader_function=fake_loader,minimum_rows=200,expected_frequency='B')
    register_dataset_splitter(infrastructure.services,minimum_training_rows=200,minimum_validation_rows=50)
    infrastructure.services.register_instance('walkforward_window_generator',FakeWindowGenerator(),replace=True)
    engine=register_historical_engine(infrastructure.services)
    result=engine.run('1155.KL')
    assert result.symbol=='1155.KL'
    assert result.windows_generated==3
    assert result.splits_created==3
    assert len(result.splits)==3
    assert result.metadata['dataset_rows']>1000
    for split in result.splits:
        assert split.training.end < split.validation.start
        assert split.training.rows>=200
        assert split.validation.rows>=50
    assert infrastructure.services.resolve('historical_engine') is engine
    rendered=HistoricalReport(result).render_text()
    assert 'BURSAAI HISTORICAL ENGINE REPORT' in rendered
    assert 'Windows Generated   : 3' in rendered
    print('='*90)
    print('BURSAAI v6.0 SPRINT 6F.2C TEST')
    print('='*90)
    print('Historical Dataset Builder : OK')
    print('Window Generator Integration: OK')
    print('Dataset Splitter Integration: OK')
    print('Split Validation            : OK')
    print('Historical Engine           : OK')
    print('Historical Result Model     : OK')
    print('Historical Report           : OK')
    print('Service Registration        : OK')
    print('='*90)
    print('SPRINT 6F.2C HISTORICAL ENGINE OK')

if __name__=='__main__': main()
