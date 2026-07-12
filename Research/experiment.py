from __future__ import annotations
import json,uuid
from dataclasses import dataclass,field,asdict
from pathlib import Path
from typing import Any,Dict,List,Optional
from Research.candidate import Candidate,normalize_for_json,utc_now_iso
from Research.enums import CandidateStatus,ExperimentMode,ExperimentStatus,SearchMethod
@dataclass
class Experiment:
    name:str; description:str=''; experiment_id:str=field(default_factory=lambda:f'EXP-{uuid.uuid4().hex[:12].upper()}')
    status:ExperimentStatus=ExperimentStatus.CREATED; mode:ExperimentMode=ExperimentMode.SEQUENTIAL; search_method:SearchMethod=SearchMethod.GRID
    candidates:List[Candidate]=field(default_factory=list); objective_metric:str='final_score'; maximize_objective:bool=True
    symbols:List[str]=field(default_factory=list); timeframe:str='1d'; start_date:Optional[str]=None; end_date:Optional[str]=None
    walk_forward_enabled:bool=True; metadata:Dict[str,Any]=field(default_factory=dict); created_at:str=field(default_factory=utc_now_iso)
    updated_at:str=field(default_factory=utc_now_iso); started_at:Optional[str]=None; completed_at:Optional[str]=None; error_message:Optional[str]=None
    def __post_init__(self):
        self.name=str(self.name).strip()
        if not self.name: raise ValueError('Experiment name tidak boleh kosong.')
        self.status=self.status if isinstance(self.status,ExperimentStatus) else ExperimentStatus(str(self.status))
        self.mode=self.mode if isinstance(self.mode,ExperimentMode) else ExperimentMode(str(self.mode))
        self.search_method=self.search_method if isinstance(self.search_method,SearchMethod) else SearchMethod(str(self.search_method))
        self.candidates=[x if isinstance(x,Candidate) else Candidate.from_dict(x) for x in self.candidates]
        self.symbols=sorted({str(x).strip().upper() for x in self.symbols if str(x).strip()}); self._validate_unique()
    def _validate_unique(self):
        ids=set(); hashes=set()
        for c in self.candidates:
            if c.candidate_id in ids or c.candidate_hash in hashes: raise ValueError('Candidate ID/hash pendua.')
            ids.add(c.candidate_id); hashes.add(c.candidate_hash)
    def _touch(self): self.updated_at=utc_now_iso()
    def add_candidate(self,candidate,allow_duplicate_hash=False):
        if any(c.candidate_id==candidate.candidate_id for c in self.candidates): raise ValueError('Candidate ID sudah wujud.')
        if any(c.candidate_hash==candidate.candidate_hash for c in self.candidates) and not allow_duplicate_hash:return False
        self.candidates.append(candidate); self.status=ExperimentStatus.READY if self.status==ExperimentStatus.CREATED else self.status; self._touch(); return True
    def start(self):
        if not self.candidates:raise RuntimeError('Experiment tiada candidate.')
        self.status=ExperimentStatus.RUNNING; self.started_at=self.started_at or utc_now_iso(); self.completed_at=None; self.error_message=None; self._touch()
    def pause(self):
        if self.status!=ExperimentStatus.RUNNING:raise RuntimeError('Hanya RUNNING boleh dipause.')
        self.status=ExperimentStatus.PAUSED; self._touch()
    def resume(self):
        if self.status not in {ExperimentStatus.PAUSED,ExperimentStatus.FAILED}:raise RuntimeError('Hanya PAUSED/FAILED boleh resume.')
        self.status=ExperimentStatus.RUNNING; self.error_message=None; self._touch()
    def cancel(self):
        self.status=ExperimentStatus.CANCELLED; self.completed_at=utc_now_iso()
        for c in self.candidates:
            if c.status in {CandidateStatus.PENDING,CandidateStatus.QUEUED,CandidateStatus.RUNNING}:c.mark_cancelled()
        self._touch()
    def finalize(self):
        if not self.candidates or any(not c.is_terminal() for c in self.candidates):raise RuntimeError('Masih ada candidate belum selesai.')
        self.status=ExperimentStatus.COMPLETED; self.completed_at=utc_now_iso(); self.error_message=None; self._touch()
    @property
    def total_candidates(self):return len(self.candidates)
    @property
    def completed_candidates(self):return sum(c.status==CandidateStatus.COMPLETED for c in self.candidates)
    @property
    def failed_candidates(self):return sum(c.status==CandidateStatus.FAILED for c in self.candidates)
    @property
    def pending_candidates(self):return sum(c.status in {CandidateStatus.PENDING,CandidateStatus.QUEUED} for c in self.candidates)
    def progress_percentage(self):return round(sum(c.is_terminal() for c in self.candidates)/len(self.candidates)*100,2) if self.candidates else 0.0
    def best_candidate(self):
        done=[c for c in self.candidates if c.status==CandidateStatus.COMPLETED]
        return sorted(done,key=lambda c:float(getattr(c.metrics,self.objective_metric)),reverse=self.maximize_objective)[0] if done else None
    def summary(self):
        b=self.best_candidate(); return {'experiment_id':self.experiment_id,'name':self.name,'status':self.status.value,'total_candidates':self.total_candidates,'completed_candidates':self.completed_candidates,'failed_candidates':self.failed_candidates,'pending_candidates':self.pending_candidates,'progress_percentage':self.progress_percentage(),'best_candidate_id':b.candidate_id if b else None,'best_score':getattr(b.metrics,self.objective_metric,None) if b else None}
    def to_dict(self):
        d=asdict(self); d['status']=self.status.value; d['mode']=self.mode.value; d['search_method']=self.search_method.value; d['candidates']=[c.to_dict() for c in self.candidates]; return normalize_for_json(d)
    @classmethod
    def from_dict(cls,d):
        return cls(experiment_id=d.get('experiment_id',f'EXP-{uuid.uuid4().hex[:12].upper()}'),name=d['name'],description=d.get('description',''),status=ExperimentStatus(d.get('status','CREATED')),mode=ExperimentMode(d.get('mode','SEQUENTIAL')),search_method=SearchMethod(d.get('search_method','GRID')),candidates=[Candidate.from_dict(c) for c in d.get('candidates',[])],objective_metric=d.get('objective_metric','final_score'),maximize_objective=bool(d.get('maximize_objective',True)),symbols=d.get('symbols',[]),timeframe=d.get('timeframe','1d'),start_date=d.get('start_date'),end_date=d.get('end_date'),walk_forward_enabled=bool(d.get('walk_forward_enabled',True)),metadata=d.get('metadata',{}),created_at=d.get('created_at',utc_now_iso()),updated_at=d.get('updated_at',utc_now_iso()),started_at=d.get('started_at'),completed_at=d.get('completed_at'),error_message=d.get('error_message'))
    def save_json(self,file_path):
        p=Path(file_path); p=p if p.suffix.lower()=='.json' else p.with_suffix('.json'); p.parent.mkdir(parents=True,exist_ok=True); t=p.with_suffix(p.suffix+'.tmp'); t.write_text(json.dumps(self.to_dict(),indent=2,ensure_ascii=False,sort_keys=True),encoding='utf-8'); t.replace(p); return p
    @classmethod
    def load_json(cls,file_path):return cls.from_dict(json.loads(Path(file_path).read_text(encoding='utf-8')))
