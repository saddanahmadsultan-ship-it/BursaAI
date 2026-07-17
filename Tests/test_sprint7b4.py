from __future__ import annotations
import tempfile, unittest
from pathlib import Path
from MachineLearning import ActiveModelRegistry, ConfidenceCalibrator, FeatureSchema, MLDataset, MLModelFactory, MLPredictionService, ModelTrainingSuite, PredictionReport, ResearchMLPromotionIntegrator

class TestSprint7B4(unittest.TestCase):
    def dataset(self):
        from MachineLearning.feature_engineering import ResearchFeatureEngineer
        names=list(ResearchFeatureEngineer.BASE_FEATURES+ResearchFeatureEngineer.ENGINEERED_FEATURES)
        s=FeatureSchema.from_names(names,target_name='promoted'); records=[]; engineer=ResearchFeatureEngineer()
        for i in range(120):
            pos=i>=60; b=82+(i%8) if pos else 30+(i%12)
            raw={'overall_score':b,'performance_score':b-2,'risk_score':b-3,'consistency_score':b+1,'robustness_score':b+2,'confidence_score':b,'cagr':22 if pos else 3,'sharpe_ratio':1.8 if pos else .2,'sortino_ratio':2.2 if pos else .3,'max_drawdown':9 if pos else 38,'volatility':14 if pos else 40,'profit_factor':1.9 if pos else .8,'recovery_factor':2.5 if pos else .2,'win_rate':62 if pos else 36,'total_trades':100,'pareto_front':1 if pos else 5,'crowding_distance':2}
            row=engineer.transform(raw); row['promoted']=1 if pos else 0; records.append(row)
        return MLDataset.from_records(s,records)
    def prepare(self,temp):
        out=Path(temp)/'models'; result=ModelTrainingSuite(out).run(self.dataset()); best=result['best_model']; ActiveModelRegistry(out).promote_champion(best.model_path,best.model_name,best.selection_score,self.dataset().feature_names); return out
    def raw(self,strong=True):
        b=88 if strong else 30
        return {'overall_score':b,'performance_score':b,'risk_score':b,'consistency_score':b,'robustness_score':b,'confidence_score':b,'cagr':25 if strong else 2,'sharpe_ratio':2 if strong else .1,'sortino_ratio':2.5 if strong else .2,'max_drawdown':8 if strong else 40,'volatility':15 if strong else 42,'profit_factor':2 if strong else .8,'recovery_factor':3 if strong else .1,'win_rate':65 if strong else 35,'total_trades':100,'pareto_front':1 if strong else 5,'crowding_distance':2}
    def test_calibration(self): self.assertTrue(0<ConfidenceCalibrator().calibrate(.9)<1)
    def test_registry(self):
        with tempfile.TemporaryDirectory() as t: self.assertIn('champion',ActiveModelRegistry(self.prepare(t)).load_manifest())
    def test_prediction(self):
        with tempfile.TemporaryDirectory() as t: self.assertIn(MLPredictionService(self.prepare(t)).predict('C1',self.raw()).decision,{'PROMOTE_TO_PAPER_TRADING','ADVANCE_TO_STRESS_TEST'})
    def test_rejection(self):
        with tempfile.TemporaryDirectory() as t: self.assertIn(MLPredictionService(self.prepare(t)).predict('C2',self.raw(False)).decision,{'REJECT_FROM_PROMOTION','REVIEW_AND_RETUNE'})
    def test_cache(self):
        with tempfile.TemporaryDirectory() as t:
            s=MLPredictionService(self.prepare(t)); s.predict('C1',self.raw()); self.assertTrue(s.predict('C1',self.raw()).cache_hit)
    def test_integrator(self):
        with tempfile.TemporaryDirectory() as t:
            svc=MLPredictionService(self.prepare(t)); x={'candidate_id':'C1','breakdown':{'overall_score':88,'performance_score':88,'risk_score':88,'consistency_score':88,'robustness_score':88,'confidence_score':88},'metrics':self.raw()}; self.assertIn('final_action',ResearchMLPromotionIntegrator(svc).evaluate(x))
    def test_report(self):
        with tempfile.TemporaryDirectory() as t:
            p=MLPredictionService(self.prepare(t)).predict('C1',self.raw()); out=PredictionReport(Path(t)/'reports').export([p]); self.assertTrue(all(x.exists() for x in out.values()))
    def test_manifest_feature_names(self):
        with tempfile.TemporaryDirectory() as t: self.assertEqual(len(ActiveModelRegistry(self.prepare(t)).load_manifest()['champion']['feature_names']),27)
if __name__=='__main__': unittest.main(verbosity=2)
