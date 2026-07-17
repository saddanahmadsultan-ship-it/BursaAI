from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, Iterable

from TradingIntelligence.position_contracts import PositionPlan


class PositionIntelligenceReport:
    def __init__(
        self,
        output_dir: str | Path = "Reports/PositionIntelligence",
    ) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(
        self,
        plans: Iterable[PositionPlan],
    ) -> Dict[str, Path]:
        items = list(plans)

        json_path = self.output_dir / "position_plans.json"
        csv_path = self.output_dir / "position_plans.csv"
        summary_path = self.output_dir / "position_summary.json"

        json_path.write_text(
            json.dumps(
                [item.to_dict() for item in items],
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

        fieldnames = [
            "symbol",
            "action",
            "approved",
            "entry_price",
            "stop_loss",
            "target_price",
            "risk_reward",
            "quantity",
            "lot_count",
            "position_value",
            "position_percent",
            "capital_at_risk",
            "risk_percent",
            "quality_score",
            "ml_probability",
            "confidence",
            "signal",
            "reasons",
        ]

        with open(
            csv_path,
            "w",
            newline="",
            encoding="utf-8-sig",
        ) as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=fieldnames,
            )
            writer.writeheader()

            for item in items:
                row = item.to_dict()
                row["reasons"] = " | ".join(item.reasons)
                writer.writerow(row)

        approved = [item for item in items if item.approved]

        summary = {
            "total_candidates": len(items),
            "approved_positions": len(approved),
            "rejected_positions": len(items) - len(approved),
            "total_position_value": round(
                sum(item.position_value for item in approved),
                2,
            ),
            "total_capital_at_risk": round(
                sum(item.capital_at_risk for item in approved),
                2,
            ),
            "average_quality_score": round(
                (
                    sum(item.quality_score for item in items)
                    / len(items)
                )
                if items
                else 0.0,
                4,
            ),
        }

        summary_path.write_text(
            json.dumps(
                summary,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

        return {
            "json": json_path,
            "csv": csv_path,
            "summary": summary_path,
        }
