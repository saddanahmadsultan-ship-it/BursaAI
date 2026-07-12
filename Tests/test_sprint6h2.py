from pathlib import Path
import sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from Framework.context import AnalysisContext
from Framework.infrastructure import build_infrastructure
from Journal.journal_services import register_trade_journal
from Trading.paper_services import register_paper_trading
from Release.soak_test import PaperTradingSoakTest
from Release.soak_report import SoakReport

def context_for(i):
    c=AnalysisContext(symbol=f"TEST{i}.KL")
    c.analysis.identity.price=10.0
    c.analysis.trade.entry=10.0
    c.analysis.portfolio.status="ALLOCATED"
    c.analysis.portfolio.allocated_shares=100
    c.analysis.portfolio.allocated_capital=1000
    return c

def main():
    infra=build_infrastructure()
    portfolio=register_paper_trading(
        infra.services,starting_capital=100000,
        commission_function=lambda order:1.0,slippage_percent=0.0
    )
    with tempfile.TemporaryDirectory() as folder:
        journal=register_trade_journal(
            infra.services,database_path=str(Path(folder)/"journal.db"),
            attach_events=True
        )
        account=infra.services.resolve("paper_account")
        engine=infra.services.resolve("paper_execution_engine")
        result=PaperTradingSoakTest(
            portfolio,account,engine,journal,
            lambda i:[context_for(i)],
            lambda i:{f"TEST{i}.KL":10.10},
            max_positions=2
        ).run(25)

        assert result.success
        assert result.completed==25
        assert result.failed==0
        assert result.duplicate_orders==0
        assert result.journal_inconsistencies==0
        assert result.peak_positions<=1
        assert result.ending_cash>0 and result.ending_equity>0

        report=SoakReport(result)
        assert "BURSAAI RC1 PAPER-TRADING SOAK REPORT" in report.render_text()
        paths=report.export(folder)
        assert Path(paths["text"]).exists() and Path(paths["json"]).exists()

    print("="*92)
    print("BURSAAI v6.0 SPRINT 6H.2 TEST")
    print("="*92)
    print("Repeated Paper Orders    : OK")
    print("Position Close Cycle     : OK")
    print("Duplicate Order Check    : OK")
    print("Journal Consistency      : OK")
    print("Cash / Equity Validation : OK")
    print("Soak Report              : OK")
    print("="*92)
    print("SPRINT 6H.2 RC1 PAPER-TRADING SOAK TEST OK")

if __name__=="__main__": main()
