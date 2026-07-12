from dataclasses import dataclass, asdict, field
from time import perf_counter
from typing import Any, Dict, List

@dataclass
class Iteration:
    iteration:int
    success:bool
    orders:int
    journal:int
    cash:float
    equity:float
    active_positions:int
    error:str=""
    duration_ms:float=0.0
    def to_dict(self): return asdict(self)

@dataclass
class SoakResult:
    requested:int
    completed:int
    failed:int
    duplicate_orders:int
    journal_inconsistencies:int
    peak_positions:int
    starting_cash:float
    ending_cash:float
    ending_equity:float
    realized_pnl:float
    unrealized_pnl:float
    duration_ms:float
    iterations:List[Iteration]=field(default_factory=list)
    @property
    def success(self):
        return self.completed==self.requested and self.failed==0 and self.duplicate_orders==0 and self.journal_inconsistencies==0
    def to_dict(self):
        return {
            "requested":self.requested,"completed":self.completed,
            "failed":self.failed,"duplicate_orders":self.duplicate_orders,
            "journal_inconsistencies":self.journal_inconsistencies,
            "peak_positions":self.peak_positions,
            "starting_cash":self.starting_cash,"ending_cash":self.ending_cash,
            "ending_equity":self.ending_equity,
            "realized_pnl":self.realized_pnl,
            "unrealized_pnl":self.unrealized_pnl,
            "duration_ms":round(self.duration_ms,4),
            "success":self.success,
            "iterations":[x.to_dict() for x in self.iterations],
        }

class PaperTradingSoakTest:
    def __init__(self,portfolio,account,engine,journal,context_factory,price_factory,max_positions=5):
        self.portfolio=portfolio; self.account=account; self.engine=engine
        self.journal=journal; self.context_factory=context_factory
        self.price_factory=price_factory; self.max_positions=max_positions

    def active_positions(self):
        return sum(1 for p in self.account.positions.values() if getattr(p,"shares",0)>0)

    def close_all(self,prices):
        for symbol,p in list(self.account.positions.items()):
            if getattr(p,"shares",0)>0:
                price=float(prices.get(symbol,getattr(p,"market_price",getattr(p,"average_price",0))))
                self.portfolio.close_position(symbol,price)

    def run(self,iterations=100):
        iterations=max(int(iterations),1)
        started=perf_counter()
        start_cash=float(self.account.cash)
        rows=[]; duplicate=0; journal_bad=0; peak=self.active_positions()

        for i in range(1,iterations+1):
            t=perf_counter(); success=True; error=""
            before_journal=self.journal.count() if self.journal else 0
            try:
                contexts=list(self.context_factory(i))
                if contexts: self.portfolio.open_allocated_positions(contexts)
                prices=dict(self.price_factory(i))
                if prices:
                    self.portfolio.update_prices(prices)
                    self.close_all(prices)
            except Exception as exc:
                success=False; error=f"{type(exc).__name__}: {exc}"

            ids=[str(o.order_id) for o in self.engine.orders]
            if len(ids)!=len(set(ids)):
                duplicate+=1; success=False

            after_journal=self.journal.count() if self.journal else 0
            if after_journal<before_journal:
                journal_bad+=1; success=False

            active=self.active_positions(); peak=max(peak,active)
            if float(self.account.cash)<0 or float(self.account.equity)<0 or active>self.max_positions:
                success=False

            rows.append(Iteration(
                i,success,len(ids),after_journal,float(self.account.cash),
                float(self.account.equity),active,error,
                (perf_counter()-t)*1000
            ))

        failed=sum(1 for x in rows if not x.success)
        return SoakResult(
            iterations,len(rows),failed,duplicate,journal_bad,peak,start_cash,
            float(self.account.cash),float(self.account.equity),
            float(self.account.realized_pnl),float(self.account.unrealized_pnl),
            (perf_counter()-started)*1000,rows
        )
