import tempfile,unittest
from pathlib import Path
from MachineLearning import FeatureSchema,MLDataset,MLModelRegistry,MLTrainingPipeline,MeanThresholdClassifier
class TestSprint7B1(unittest.TestCase):
    def make_dataset(self):
        schema=FeatureSchema.from_names(["ai_score","robustness","consistency","confidence","risk_score"],"promoted")
        rec=[]
        for i in range(40):
            pos=i>=20; b=(75+i%10) if pos else (35+i%10); rec.append({"ai_score":b,"robustness":b+3,"consistency":b+5,"confidence":b+2,"risk_score":b,"promoted":1 if pos else 0,"metadata":{"candidate":f"C-{i:03d}"}})
        return MLDataset.from_records(schema,rec)
    def test_dataset_creation(self): self.assertEqual(self.make_dataset().size,40)
    def test_dataset_split(self):
        s=self.make_dataset().split(); self.assertEqual((s.train.size,s.validation.size,s.test.size),(28,6,6))
    def test_training_pipeline(self):
        with tempfile.TemporaryDirectory() as t:
            r=MLTrainingPipeline(MLModelRegistry(t)).run(self.make_dataset(),MeanThresholdClassifier()); self.assertTrue(Path(r.model_path).exists()); self.assertGreaterEqual(r.train_accuracy,.8)
    def test_model_registry_load(self):
        with tempfile.TemporaryDirectory() as t:
            reg=MLModelRegistry(t); r=MLTrainingPipeline(reg).run(self.make_dataset(),MeanThresholdClassifier()); self.assertTrue(reg.load(r.model_id).is_fitted)
    def test_missing_feature_rejected(self):
        with self.assertRaises(ValueError): MLDataset.from_records(FeatureSchema.from_names(["a","b"]),[{"a":1,"target":1}])
    def test_unfitted_model_rejected(self):
        with self.assertRaises(RuntimeError): MeanThresholdClassifier().predict_one([1,2])
    def test_registry_rejects_unfitted(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(RuntimeError): MLModelRegistry(t).save(MeanThresholdClassifier())
    def test_matrix_shape(self):
        X,y=self.make_dataset().as_matrix(); self.assertEqual((len(X),len(X[0]),len(y)),(40,5,40))
if __name__=="__main__": unittest.main(verbosity=2)
