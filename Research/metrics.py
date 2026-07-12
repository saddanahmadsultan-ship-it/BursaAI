from __future__ import annotations
from dataclasses import dataclass, asdict
from math import isfinite
from typing import Any, Dict

def _f(v, d=0.0):
    try:
        x=float(v); return x if isfinite(x) else d
    except (TypeError,ValueError): return d

def _i(v,d=0):
    try:return int(v)
    except (TypeError,ValueError):return d

@dataclass
class PerformanceMetrics:
    total_return:float=0.0; cagr:float=0.0; sharpe_ratio:float=0.0; sortino_ratio:float=0.0; calmar_ratio:float=0.0
    max_drawdown:float=0.0; volatility:float=0.0; win_rate:float=0.0; profit_factor:float=0.0; expectancy:float=0.0
    payoff_ratio:float=0.0; recovery_factor:float=0.0; exposure:float=0.0; total_trades:int=0; winning_trades:int=0; losing_trades:int=0
    average_win:float=0.0; average_loss:float=0.0; largest_win:float=0.0; largest_loss:float=0.0; average_holding_days:float=0.0
    consistency_score:float=0.0; robustness_score:float=0.0; risk_score:float=0.0; stability_score:float=0.0; final_score:float=0.0
    def __post_init__(self):
        ints={'total_trades','winning_trades','losing_trades'}
        for n in self.__dataclass_fields__:
            setattr(self,n,max(0,_i(getattr(self,n))) if n in ints else _f(getattr(self,n)))
        self.max_drawdown=abs(self.max_drawdown); self.volatility=abs(self.volatility)
        self.win_rate=min(100,max(0,self.win_rate)); self.exposure=min(100,max(0,self.exposure))
        for n in ('consistency_score','robustness_score','risk_score','stability_score','final_score'):
            setattr(self,n,min(100,max(0,getattr(self,n))))
    def validate_trade_counts(self): return self.winning_trades+self.losing_trades<=self.total_trades
    def to_dict(self)->Dict[str,Any]: return asdict(self)
    @classmethod
    def from_dict(cls,data):
        if not data:return cls()
        return cls(**{k:v for k,v in data.items() if k in cls.__dataclass_fields__})
