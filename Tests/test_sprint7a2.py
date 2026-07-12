import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from Research import CandidateStatus,Experiment,ExperimentRegistry,ExperimentStatus,ParameterSpace,PerformanceMetrics
from Research.checkpoint import CheckpointError
class T(unittest.TestCase):
 def build(self):return Experiment(name='Registry Test',candidates=ParameterSpace('EMA_RSI',{'ema_fast':[10,20],'ema_slow':[50],'rsi_period':[8,14]}).generate_grid_candidates(symbol='1155.KL'),symbols=['1155.KL'])
 def test_register_load(self):
  with tempfile.TemporaryDirectory() as d:r=ExperimentRegistry(Path(d)/'Experiments');e=self.build();r.register(e);self.assertEqual(r.load(e.experiment_id).experiment_id,e.experiment_id);self.assertEqual(len(r.list()),1)
 def test_duplicate(self):
  with tempfile.TemporaryDirectory() as d:
   r=ExperimentRegistry(Path(d)/'Experiments');e=self.build();r.register(e)
   with self.assertRaises(Exception):r.register(e)
 def test_checkpoint(self):
  with tempfile.TemporaryDirectory() as d:r=ExperimentRegistry(Path(d)/'Experiments');e=self.build();r.register(e);self.assertEqual(r.checkpoints.load(e.experiment_id).experiment_id,e.experiment_id)
 def test_tamper(self):
  with tempfile.TemporaryDirectory() as d:
   r=ExperimentRegistry(Path(d)/'Experiments');e=self.build();r.register(e);p=r.checkpoints.checkpoint_path(e.experiment_id);p.write_text(p.read_text()+' ',encoding='utf-8')
   with self.assertRaises(CheckpointError):r.checkpoints.load(e.experiment_id)
 def test_pause_resume_cancel(self):
  with tempfile.TemporaryDirectory() as d:r=ExperimentRegistry(Path(d)/'Experiments');e=self.build();e.start();r.register(e);self.assertEqual(r.pause(e.experiment_id).status,ExperimentStatus.PAUSED);self.assertEqual(r.resume(e.experiment_id).status,ExperimentStatus.RUNNING);c=r.cancel(e.experiment_id);self.assertTrue(all(x.status==CandidateStatus.CANCELLED for x in c.candidates))
 def test_recover(self):
  with tempfile.TemporaryDirectory() as d:r=ExperimentRegistry(Path(d)/'Experiments');e=self.build();e.start();r.register(e);self.assertEqual(r.recover(e.experiment_id).status,ExperimentStatus.PAUSED)
 def test_progress(self):
  with tempfile.TemporaryDirectory() as d:r=ExperimentRegistry(Path(d)/'Experiments');e=self.build();r.register(e);e.candidates[0].mark_completed(PerformanceMetrics(final_score=88));r.save(e,'candidate_completed');self.assertEqual(r.load(e.experiment_id).completed_candidates,1)
 def test_filter(self):
  with tempfile.TemporaryDirectory() as d:r=ExperimentRegistry(Path(d)/'Experiments');e=self.build();r.register(e);self.assertEqual(len(r.list(ExperimentStatus.CREATED)),1)
 def test_rebuild(self):
  with tempfile.TemporaryDirectory() as d:r=ExperimentRegistry(Path(d)/'Experiments');e=self.build();r.register(e);r.manifest_path.write_text('{}');self.assertEqual(r.rebuild_manifest(),1);self.assertEqual(len(r.list()),1)
 def test_delete(self):
  with tempfile.TemporaryDirectory() as d:r=ExperimentRegistry(Path(d)/'Experiments');e=self.build();r.register(e);self.assertTrue(r.delete(e.experiment_id));self.assertEqual(r.list(),[])
if __name__=='__main__':unittest.main(verbosity=2)
