from __future__ import annotations
import time, traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional
from Research.candidate import Candidate
from Research.enums import CandidateStatus, ExperimentMode, ExperimentStatus
from Research.experiment import Experiment
from Research.experiment_registry import ExperimentRegistry
from Research.metrics import PerformanceMetrics

CandidateEvaluator = Callable[[Candidate], PerformanceMetrics | Dict[str, Any]]

@dataclass
class RunnerConfig:
    max_workers: int = 4
    checkpoint_every: int = 1
    max_retries: int = 1
    retry_delay_seconds: float = 0.0
    fail_fast: bool = False
    def __post_init__(self):
        self.max_workers=max(1,int(self.max_workers)); self.checkpoint_every=max(1,int(self.checkpoint_every))
        self.max_retries=max(0,int(self.max_retries)); self.retry_delay_seconds=max(0.0,float(self.retry_delay_seconds))

@dataclass
class RunnerStats:
    total:int=0; completed:int=0; failed:int=0; skipped:int=0; cancelled:int=0; retries:int=0
    elapsed_seconds:float=0.0; started_at_monotonic:float=field(default_factory=time.monotonic)
    @property
    def processed(self): return self.completed+self.failed+self.skipped+self.cancelled
    @property
    def progress_percentage(self): return round(self.processed/self.total*100,2) if self.total else 0.0
    def finish(self): self.elapsed_seconds=max(0.0,time.monotonic()-self.started_at_monotonic)
    def to_dict(self):
        return {"total":self.total,"completed":self.completed,"failed":self.failed,"skipped":self.skipped,
                "cancelled":self.cancelled,"retries":self.retries,"processed":self.processed,
                "progress_percentage":self.progress_percentage,"elapsed_seconds":round(self.elapsed_seconds,4)}

class ExperimentRunner:
    def __init__(self, registry:ExperimentRegistry, evaluator:CandidateEvaluator, config:Optional[RunnerConfig]=None):
        if not isinstance(registry,ExperimentRegistry): raise TypeError("registry mesti ExperimentRegistry.")
        if not callable(evaluator): raise TypeError("evaluator mesti callable.")
        self.registry=registry; self.evaluator=evaluator; self.config=config or RunnerConfig()

    def run(self, experiment_or_id:Experiment|str, *, resume:bool=True)->RunnerStats:
        exp=self._resolve(experiment_or_id)
        if exp.status==ExperimentStatus.CANCELLED: raise RuntimeError("Experiment CANCELLED tidak boleh dijalankan.")
        if exp.status==ExperimentStatus.COMPLETED: return self._existing_stats(exp)
        if exp.status==ExperimentStatus.RUNNING and resume: exp.status=ExperimentStatus.PAUSED
        if exp.status in {ExperimentStatus.PAUSED,ExperimentStatus.FAILED}: exp.resume()
        elif exp.status in {ExperimentStatus.CREATED,ExperimentStatus.READY}: exp.start()
        self.registry.save(exp,checkpoint_reason="runner_start")
        runnable=[c for c in exp.candidates if c.status in {CandidateStatus.PENDING,CandidateStatus.QUEUED,CandidateStatus.FAILED}]
        stats=RunnerStats(total=len(runnable))
        try:
            if exp.mode==ExperimentMode.PARALLEL: self._run_parallel(exp,runnable,stats)
            else: self._run_sequential(exp,runnable,stats)
            if exp.status!=ExperimentStatus.CANCELLED:
                if all(c.is_terminal() for c in exp.candidates): exp.finalize()
                else: exp.status=ExperimentStatus.PAUSED; exp._touch()
            stats.finish(); exp.metadata["last_runner_stats"]=stats.to_dict()
            self.registry.save(exp,checkpoint_reason="runner_finished")
            return stats
        except Exception as exc:
            stats.finish(); exp.status=ExperimentStatus.FAILED; exp.error_message=str(exc); exp._touch(); exp.metadata["last_runner_stats"]=stats.to_dict(); exp.metadata["runner_traceback"]=traceback.format_exc()
            self.registry.save(exp,checkpoint_reason="runner_failed"); raise

    def _run_sequential(self,exp:Experiment,candidates:Iterable[Candidate],stats:RunnerStats):
        n=0
        for c in candidates:
            self._evaluate(c,stats); n+=1
            if n>=self.config.checkpoint_every:
                self.registry.save(exp,checkpoint_reason="batch_progress"); n=0
            if self.config.fail_fast and c.status==CandidateStatus.FAILED: raise RuntimeError(f"Fail-fast: {c.candidate_id}")

    def _run_parallel(self,exp:Experiment,candidates:List[Candidate],stats:RunnerStats):
        for c in candidates:
            if c.status==CandidateStatus.FAILED: c.reset()
            c.mark_queued()
        self.registry.save(exp,checkpoint_reason="parallel_queue")
        n=0
        with ThreadPoolExecutor(max_workers=self.config.max_workers,thread_name_prefix="BursaAI-Research") as executor:
            fmap={executor.submit(self._evaluate,c,stats):c for c in candidates}
            for future in as_completed(fmap):
                try: future.result()
                except Exception:
                    if self.config.fail_fast:
                        for f in fmap: f.cancel()
                        raise
                n+=1
                if n>=self.config.checkpoint_every:
                    self.registry.save(exp,checkpoint_reason="parallel_progress"); n=0

    def _evaluate(self,c:Candidate,stats:RunnerStats):
        if c.status==CandidateStatus.COMPLETED: stats.skipped+=1; return
        attempts=0
        while True:
            attempts+=1; c.mark_running()
            try:
                result=self.evaluator(c)
                if isinstance(result,dict): result=PerformanceMetrics.from_dict(result)
                if not isinstance(result,PerformanceMetrics): raise TypeError("Evaluator mesti pulangkan PerformanceMetrics atau dictionary.")
                c.mark_completed(result); stats.completed+=1; return
            except Exception as exc:
                if attempts<=self.config.max_retries:
                    stats.retries+=1
                    if self.config.retry_delay_seconds: time.sleep(self.config.retry_delay_seconds)
                    continue
                c.mark_failed(str(exc)); stats.failed+=1
                if self.config.fail_fast: raise
                return

    def _resolve(self,x):
        if isinstance(x,Experiment): return x
        if isinstance(x,str): return self.registry.load(x)
        raise TypeError("experiment_or_id mesti Experiment atau experiment_id.")

    @staticmethod
    def _existing_stats(exp):
        s=RunnerStats(total=exp.total_candidates)
        for c in exp.candidates:
            if c.status==CandidateStatus.COMPLETED:s.completed+=1
            elif c.status==CandidateStatus.FAILED:s.failed+=1
            elif c.status==CandidateStatus.SKIPPED:s.skipped+=1
            elif c.status==CandidateStatus.CANCELLED:s.cancelled+=1
        s.finish(); return s
