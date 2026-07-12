from __future__ import annotations
import hashlib,json,uuid
from dataclasses import dataclass,field,asdict
from datetime import datetime,timezone
from typing import Any,Dict,List,Optional
from Research.enums import CandidateStatus
from Research.metrics import PerformanceMetrics

def utc_now_iso(): return datetime.now(timezone.utc).isoformat()
def normalize_for_json(v):
    if isinstance(v,dict): return {str(k):normalize_for_json(x) for k,x in sorted(v.items(),key=lambda p:str(p[0]))}
    if isinstance(v,(list,tuple)): return [normalize_for_json(x) for x in v]
    if isinstance(v,set): return sorted([normalize_for_json(x) for x in v],key=lambda x:json.dumps(x,sort_keys=True,default=str))
    if hasattr(v,'item'):
        try:return v.item()
        except Exception:pass
    if isinstance(v,(str,int,float,bool,type(None))):return v
    return str(v)
@dataclass
class Candidate:
    name:str; strategy_name:str; parameters:Dict[str,Any]
    candidate_id:str=field(default_factory=lambda:f'CAN-{uuid.uuid4().hex[:12].upper()}')
    status:CandidateStatus=CandidateStatus.PENDING; metrics:PerformanceMetrics=field(default_factory=PerformanceMetrics)
    symbol:Optional[str]=None; timeframe:str='1d'; tags:List[str]=field(default_factory=list); notes:str=''; rank:Optional[int]=None
    error_message:Optional[str]=None; created_at:str=field(default_factory=utc_now_iso); started_at:Optional[str]=None; completed_at:Optional[str]=None
    candidate_hash:str=field(init=False)
    def __post_init__(self):
        self.name=str(self.name).strip(); self.strategy_name=str(self.strategy_name).strip(); self.timeframe=str(self.timeframe).strip() or '1d'
        if not self.name or not self.strategy_name: raise ValueError('Candidate/strategy name tidak boleh kosong.')
        if not isinstance(self.parameters,dict): raise TypeError('parameters mesti dictionary.')
        if not isinstance(self.status,CandidateStatus): self.status=CandidateStatus(str(self.status))
        if isinstance(self.metrics,dict): self.metrics=PerformanceMetrics.from_dict(self.metrics)
        self.parameters=normalize_for_json(self.parameters); self.tags=sorted({str(x).strip() for x in self.tags if str(x).strip()}); self.candidate_hash=self.generate_hash()
    def generate_hash(self):
        payload=json.dumps({'strategy_name':self.strategy_name,'parameters':self.parameters,'symbol':self.symbol,'timeframe':self.timeframe},sort_keys=True,separators=(',',':'),ensure_ascii=False,default=str)
        return hashlib.sha256(payload.encode()).hexdigest()
    def mark_queued(self): self.status=CandidateStatus.QUEUED
    def mark_running(self): self.status=CandidateStatus.RUNNING; self.started_at=utc_now_iso(); self.completed_at=None; self.error_message=None
    def mark_completed(self,metrics): self.metrics=metrics if isinstance(metrics,PerformanceMetrics) else PerformanceMetrics.from_dict(metrics); self.status=CandidateStatus.COMPLETED; self.completed_at=utc_now_iso(); self.error_message=None
    def mark_failed(self,msg): self.status=CandidateStatus.FAILED; self.completed_at=utc_now_iso(); self.error_message=str(msg)
    def mark_cancelled(self): self.status=CandidateStatus.CANCELLED; self.completed_at=utc_now_iso()
    def reset(self): self.status=CandidateStatus.PENDING; self.metrics=PerformanceMetrics(); self.rank=None; self.error_message=None; self.started_at=None; self.completed_at=None
    def is_terminal(self): return self.status in {CandidateStatus.COMPLETED,CandidateStatus.FAILED,CandidateStatus.CANCELLED,CandidateStatus.SKIPPED}
    def is_successful(self): return self.status==CandidateStatus.COMPLETED
    def to_dict(self):
        d=asdict(self); d['status']=self.status.value; d['metrics']=self.metrics.to_dict(); d['candidate_hash']=self.candidate_hash; return normalize_for_json(d)
    @classmethod
    def from_dict(cls,d):
        c=cls(candidate_id=d.get('candidate_id',f'CAN-{uuid.uuid4().hex[:12].upper()}'),name=d['name'],strategy_name=d['strategy_name'],parameters=d.get('parameters',{}),status=CandidateStatus(d.get('status','PENDING')),metrics=PerformanceMetrics.from_dict(d.get('metrics')),symbol=d.get('symbol'),timeframe=d.get('timeframe','1d'),tags=d.get('tags',[]),notes=d.get('notes',''),rank=d.get('rank'),error_message=d.get('error_message'),created_at=d.get('created_at',utc_now_iso()),started_at=d.get('started_at'),completed_at=d.get('completed_at'))
        if d.get('candidate_hash') and d['candidate_hash']!=c.candidate_hash: raise ValueError('Candidate hash tidak sepadan.')
        return c
    def clone(self,*,name=None): return Candidate(name=name or self.name,strategy_name=self.strategy_name,parameters=dict(self.parameters),symbol=self.symbol,timeframe=self.timeframe,tags=list(self.tags),notes=self.notes)
