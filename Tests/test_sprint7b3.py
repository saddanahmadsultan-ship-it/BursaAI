import tempfile,unittest
from pathlib import Path
from MachineLearning import FeatureSchema,MLDataset,ClassificationEvaluator,ModelTrainingSuite,ModelEvaluationReport
class TestSprint7B3(unittest.TestCase):
    def make_dataset(self):
        s=FeatureSchema.from_names(['overall_score','robustness_score','consistency_score','confidence_score','risk_score'],'promoted'); rows=[]
        for i in range(60):
            pos=i>=30; b=72+i%18 if pos else 30+i%24; rows.append({'overall_score':b,'robustness_score':b+3,'consistency_score':b+4,'confidence_score':b+2,'risk_score':b-1,'promoted':1 if pos else 0})
        return MLDataset.from_records(s,rows)
    def test_evaluator(self): self.assertEqual(ClassificationEvaluator.evaluate([1,1,0,0],[1,0,0,0]).true_negative,2)
    def test_training_suite(self):
        with tempfile.TemporaryDirectory() as t:self.assertEqual(len(ModelTrainingSuite(t).run(self.make_dataset())['ranked_results']),4)
    def test_model_files_written(self):
        with tempfile.TemporaryDirectory() as t:
            for x in ModelTrainingSuite(t).run(self.make_dataset())['ranked_results']: self.assertTrue(Path(x.model_path).exists())
    def test_selector_orders(self):
        with tempfile.TemporaryDirectory() as t:
            r=ModelTrainingSuite(t).run(self.make_dataset())['ranked_results']; self.assertEqual([x.selection_score for x in r],sorted([x.selection_score for x in r],reverse=True))
    def test_gap_range(self):
        with tempfile.TemporaryDirectory() as t:
            for x in ModelTrainingSuite(t).run(self.make_dataset())['ranked_results']: self.assertTrue(0<=x.generalization_gap<=1)
    def test_cv_range(self):
        with tempfile.TemporaryDirectory() as t:
            for x in ModelTrainingSuite(t).run(self.make_dataset())['ranked_results']: self.assertTrue(0<=x.cross_validation_mean<=1)
    def test_report_export(self):
        with tempfile.TemporaryDirectory() as t:
            r=ModelTrainingSuite(Path(t)/'m').run(self.make_dataset())['ranked_results']; o=ModelEvaluationReport(Path(t)/'r').export(r); self.assertTrue(all(p.exists() for p in o.values()))
    def test_best_model_score(self):
        with tempfile.TemporaryDirectory() as t:self.assertGreaterEqual(ModelTrainingSuite(t).run(self.make_dataset())['best_model'].selection_score,.55)
if __name__=='__main__':unittest.main(verbosity=2)
