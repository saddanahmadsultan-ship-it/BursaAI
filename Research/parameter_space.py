from __future__ import annotations
import itertools,math,random
from dataclasses import dataclass,field
from typing import Any,Dict,Sequence,Optional
from Research.candidate import Candidate,normalize_for_json
@dataclass
class ParameterSpace:
    strategy_name:str; parameters:Dict[str,Sequence[Any]]; name_prefix:Optional[str]=None; fixed_parameters:Dict[str,Any]=field(default_factory=dict); constraints_enabled:bool=True
    def __post_init__(self):
        self.strategy_name=str(self.strategy_name).strip(); norm={}
        if not self.strategy_name:raise ValueError('strategy_name kosong.')
        for k,vals in self.parameters.items():
            if isinstance(vals,(str,bytes)):raise TypeError('Nilai parameter mesti sequence.')
            u=[]
            for v in list(vals):
                v=normalize_for_json(v)
                if v not in u:u.append(v)
            if not u:raise ValueError(f'Parameter {k} kosong.')
            norm[str(k).strip()]=u
        if set(norm)&set(self.fixed_parameters):raise ValueError('Parameter bertindih.')
        self.parameters=norm; self.fixed_parameters=normalize_for_json(self.fixed_parameters); self.name_prefix=self.name_prefix or self.strategy_name
    @property
    def parameter_names(self):return sorted(self.parameters)
    @property
    def total_combinations(self):return math.prod(len(v) for v in self.parameters.values()) if self.parameters else 1
    def validate_combination(self,c):
        if not self.constraints_enabled:return True
        for a,b in [('fast','slow'),('short','long'),('ema_fast','ema_slow'),('ma_fast','ma_slow'),('sma_fast','sma_slow'),('macd_fast','macd_slow'),('min','max'),('lower','upper'),('rsi_lower','rsi_upper')]:
            if a in c and b in c:
                try:
                    if not float(c[a])<float(c[b]):return False
                except (TypeError,ValueError):pass
        return True
    def iter_combinations(self,max_combinations=None):
        names=self.parameter_names; groups=[self.parameters[n] for n in names]; emitted=0
        for vals in itertools.product(*groups) if groups else [()]:
            c={**self.fixed_parameters,**dict(zip(names,vals))}
            if not self.validate_combination(c):continue
            yield normalize_for_json(c); emitted+=1
            if max_combinations is not None and emitted>=max_combinations:break
    def generate_grid_candidates(self,symbol=None,timeframe='1d',tags=None,max_candidates=None):
        return [Candidate(name=f'{self.name_prefix}_{i:05d}',strategy_name=self.strategy_name,parameters=p,symbol=symbol,timeframe=timeframe,tags=list(tags or [])) for i,p in enumerate(self.iter_combinations(max_candidates),1)]
    def generate_random_candidates(self,sample_size,seed=None,symbol=None,timeframe='1d',tags=None):
        combos=list(self.iter_combinations())
        if sample_size<=0 or sample_size>len(combos):raise ValueError('sample_size tidak sah.')
        return [Candidate(name=f'{self.name_prefix}_RANDOM_{i:05d}',strategy_name=self.strategy_name,parameters=p,symbol=symbol,timeframe=timeframe,tags=list(tags or [])) for i,p in enumerate(random.Random(seed).sample(combos,sample_size),1)]
