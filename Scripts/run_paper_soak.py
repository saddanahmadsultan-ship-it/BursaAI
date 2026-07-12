from pathlib import Path
import argparse,sys
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from Framework.context import AnalysisContext
from Framework.infrastructure import build_infrastructure
from Journal.journal_services import register_trade_journal
from Trading.paper_services import register_paper_trading
from Release.soak_test import PaperTradingSoakTest
from Release.soak_report import SoakReport

def context_for(i):
    c=AnalysisContext(symbol=f"SOAK{i:05d}.KL")
    c.analysis.identity.price=10.0
    c.analysis.trade.entry=10.0
    c.analysis.portfolio.status="ALLOCATED"
    c.analysis.portfolio.allocated_shares=100
    c.analysis.portfolio.allocated_capital=1000
    return c

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--iterations",type=int,default=100)
    p.add_argument("--output",default="Reports/Release")
    a=p.parse_args()

    infra=build_infrastructure()
    portfolio=register_paper_trading(
        infra.services,starting_capital=100000,
        commission_function=lambda order:1.0
    )
    journal=register_trade_journal(
        infra.services,database_path="Data/rc1_soak_journal.db",
        attach_events=True
    )
    account=infra.services.resolve("paper_account")
    engine=infra.services.resolve("paper_execution_engine")
    result=PaperTradingSoakTest(
        portfolio,account,engine,journal,
        lambda i:[context_for(i)],
        lambda i:{f"SOAK{i:05d}.KL":10.10},
        max_positions=5
    ).run(a.iterations)

    report=SoakReport(result)
    print(report.render_text())
    print(report.export(a.output))
    if not result.success: raise SystemExit(1)

if __name__=="__main__": main()
