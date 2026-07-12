from __future__ import annotations
import uuid
from dataclasses import dataclass,field,asdict
from typing import Any,Dict,List,Optional
from Research.candidate import normalize_for_json,utc_now_iso
from Research.metrics import PerformanceMetrics
@dataclass
class ResearchResult:
    experiment_id:str; candidate_id:str; candidate_hash:str; metrics:PerformanceMetrics
    result_id:str=field(default_factory=lambda:f'RES-{uuid.uuid4().hex[:12].upper()}')
    walk_forward_folds:List[Dict[str,Any]]=field(default_factory=list); monthly_returns:Dict[str,float]=field(default_factory=dict)
    yearly_returns:Dict[str,float]=field(default_factory=dict); equity_curve:List[Dict[str,Any]]=field(default_factory=list)
    trade_summary:Dict[str,Any]=field(default_factory=dict); diagnostics:Dict[str,Any]=field(default_factory=dict)
    execution_seconds:float=0.0; created_at:str=field(default_factory=utc_now_iso); error_message:Optional[str]=None
    def __post_init__(self):
        if isinstance(self.metrics,dict):self.metrics=PerformanceMetrics.from_dict(self.metrics)
        self.execution_seconds=max(0.0,float(self.execution_seconds or 0.0))
    @property
    def successful(self):return not bool(self.error_message)
    def to_dict(self):
        d=asdict(self); d['metrics']=self.metrics.to_dict(); return normalize_for_json(d)
    @classmethod
    def from_dict(cls,d):
        return cls(result_id=d.get('result_id',f'RES-{uuid.uuid4().hex[:12].upper()}'),experiment_id=d['experiment_id'],candidate_id=d['candidate_id'],candidate_hash=d['candidate_hash'],metrics=PerformanceMetrics.from_dict(d.get('metrics')),walk_forward_folds=d.get('walk_forward_folds',[]),monthly_returns=d.get('monthly_returns',{}),yearly_returns=d.get('yearly_returns',{}),equity_curve=d.get('equity_curve',[]),trade_summary=d.get('trade_summary',{}),diagnostics=d.get('diagnostics',{}),execution_seconds=d.get('execution_seconds',0.0),created_at=d.get('created_at',utc_now_iso()),error_message=d.get('error_message'))
