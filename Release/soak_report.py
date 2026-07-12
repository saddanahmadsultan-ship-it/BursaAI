import json
from pathlib import Path

class SoakReport:
    def __init__(self,result): self.result=result
    def render_text(self):
        r=self.result
        return "\n".join([
            "="*78,
            "BURSAAI RC1 PAPER-TRADING SOAK REPORT",
            "="*78,
            f"Status                  : {'PASSED' if r.success else 'FAILED'}",
            f"Iterations Requested    : {r.requested}",
            f"Iterations Completed    : {r.completed}",
            f"Failed Iterations       : {r.failed}",
            f"Duplicate Orders        : {r.duplicate_orders}",
            f"Journal Inconsistencies : {r.journal_inconsistencies}",
            f"Peak Active Positions   : {r.peak_positions}",
            f"Starting Cash           : RM{r.starting_cash:,.2f}",
            f"Ending Cash             : RM{r.ending_cash:,.2f}",
            f"Ending Equity           : RM{r.ending_equity:,.2f}",
            f"Realized P/L            : RM{r.realized_pnl:,.2f}",
            f"Unrealized P/L          : RM{r.unrealized_pnl:,.2f}",
            f"Duration                : {r.duration_ms/1000:.2f} sec",
            "="*78,
        ])
    def export(self,folder="Reports/Release"):
        folder=Path(folder); folder.mkdir(parents=True,exist_ok=True)
        txt=folder/"rc1_paper_soak_report.txt"
        js=folder/"rc1_paper_soak_report.json"
        txt.write_text(self.render_text()+"\n",encoding="utf-8")
        js.write_text(json.dumps(self.result.to_dict(),indent=2,default=str)+"\n",encoding="utf-8")
        return {"text":str(txt),"json":str(js)}
