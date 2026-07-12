import hashlib
from Research.metrics import PerformanceMetrics

def deterministic_mock_evaluator(candidate):
    seed=int(hashlib.sha256(candidate.candidate_hash.encode()).hexdigest()[:12],16)
    cagr=5+(seed%2500)/100; sharpe=.4+((seed//7)%240)/100; dd=5+((seed//11)%2200)/100
    win=35+((seed//13)%3500)/100; pf=.8+((seed//17)%170)/100; trades=20+((seed//19)%180)
    score=min(100.0,min(cagr/35,1)*30+min(sharpe/3,1)*25+max(0,1-dd/35)*20+min(win/70,1)*15+min(pf/2.5,1)*10)
    return PerformanceMetrics(cagr=cagr,sharpe_ratio=sharpe,max_drawdown=dd,win_rate=win,profit_factor=pf,total_trades=trades,final_score=score)
