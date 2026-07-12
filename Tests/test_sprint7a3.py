import sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from Research import *

class T(unittest.TestCase):
    def exp(self,mode=ExperimentMode.SEQUENTIAL,count=6):
        s=ParameterSpace("EMA_RSI",{"ema_fast":[5,10,15],"ema_slow":[50,100],"rsi_period":[8,14]})
        return Experiment(name="Runner Test",mode=mode,candidates=s.generate_grid_candidates(max_candidates=count))
    def test_sequential(self):
        with tempfile.TemporaryDirectory() as d:
            r=ExperimentRegistry(Path(d)/"Experiments"); e=self.exp(); r.register(e)
            st=ExperimentRunner(r,lambda c:PerformanceMetrics(final_score=80)).run(e)
            self.assertEqual(st.completed,6); self.assertEqual(r.load(e.experiment_id).status,ExperimentStatus.COMPLETED)
    def test_parallel(self):
        with tempfile.TemporaryDirectory() as d:
            r=ExperimentRegistry(Path(d)/"Experiments"); e=self.exp(ExperimentMode.PARALLEL); r.register(e)
            st=ExperimentRunner(r,lambda c:{"final_score":85},RunnerConfig(max_workers=3)).run(e)
            self.assertEqual(st.completed,6)
    def test_retry(self):
        with tempfile.TemporaryDirectory() as d:
            r=ExperimentRegistry(Path(d)/"Experiments"); e=self.exp(count=1); r.register(e); seen={}
            def f(c):
                seen[c.candidate_id]=seen.get(c.candidate_id,0)+1
                if seen[c.candidate_id]==1: raise RuntimeError("temp")
                return PerformanceMetrics(final_score=70)
            st=ExperimentRunner(r,f,RunnerConfig(max_retries=1)).run(e)
            self.assertEqual((st.completed,st.retries),(1,1))
    def test_failure(self):
        with tempfile.TemporaryDirectory() as d:
            r=ExperimentRegistry(Path(d)/"Experiments"); e=self.exp(count=1); r.register(e)
            st=ExperimentRunner(r,lambda c:(_ for _ in ()).throw(RuntimeError("bad")),RunnerConfig(max_retries=2)).run(e)
            self.assertEqual((st.failed,st.retries),(1,2))
    def test_resume_skips_completed(self):
        with tempfile.TemporaryDirectory() as d:
            r=ExperimentRegistry(Path(d)/"Experiments"); e=self.exp(count=3); e.candidates[0].mark_completed(PerformanceMetrics(final_score=90)); e.status=ExperimentStatus.PAUSED; r.register(e); calls=[]
            ExperimentRunner(r,lambda c:(calls.append(c.candidate_id) or PerformanceMetrics(final_score=70))).run(e.experiment_id)
            self.assertEqual(len(calls),2); self.assertEqual(r.load(e.experiment_id).completed_candidates,3)
    def test_checkpoint(self):
        with tempfile.TemporaryDirectory() as d:
            r=ExperimentRegistry(Path(d)/"Experiments"); e=self.exp(count=2); r.register(e)
            ExperimentRunner(r,lambda c:PerformanceMetrics(final_score=77),RunnerConfig(checkpoint_every=1)).run(e)
            self.assertTrue(r.checkpoints.exists(e.experiment_id))
    def test_invalid_result(self):
        with tempfile.TemporaryDirectory() as d:
            r=ExperimentRegistry(Path(d)/"Experiments"); e=self.exp(count=1); r.register(e)
            self.assertEqual(ExperimentRunner(r,lambda c:"bad").run(e).failed,1)
    def test_completed_existing(self):
        with tempfile.TemporaryDirectory() as d:
            r=ExperimentRegistry(Path(d)/"Experiments"); e=self.exp(count=2)
            [c.mark_completed(PerformanceMetrics(final_score=80)) for c in e.candidates]; e.finalize(); r.register(e)
            self.assertEqual(ExperimentRunner(r,lambda c:PerformanceMetrics()).run(e.experiment_id).completed,2)
    def test_best(self):
        with tempfile.TemporaryDirectory() as d:
            r=ExperimentRegistry(Path(d)/"Experiments"); e=self.exp(count=3); r.register(e); it=iter([60,95,80])
            ExperimentRunner(r,lambda c:PerformanceMetrics(final_score=next(it))).run(e)
            self.assertEqual(r.load(e.experiment_id).best_candidate().metrics.final_score,95)
    def test_fail_fast(self):
        with tempfile.TemporaryDirectory() as d:
            r=ExperimentRegistry(Path(d)/"Experiments"); e=self.exp(count=2); r.register(e)
            with self.assertRaises(RuntimeError): ExperimentRunner(r,lambda c:(_ for _ in ()).throw(RuntimeError("fatal")),RunnerConfig(fail_fast=True,max_retries=0)).run(e)
            self.assertEqual(r.load(e.experiment_id).status,ExperimentStatus.FAILED)
if __name__=="__main__": unittest.main(verbosity=2)
