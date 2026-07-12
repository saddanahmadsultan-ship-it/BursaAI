from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

from Research.ranking_models import RankedStrategy


class LeaderboardExporter:
    def __init__(self, output_dir: str | Path = "Reports/Ranking") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_all(
        self,
        ranked: Iterable[RankedStrategy],
    ) -> Dict[str, Path]:
        items = list(ranked)

        return {
            "json": self.export_json(items),
            "csv": self.export_csv(items),
            "summary": self.export_summary(items),
        }

    def export_json(
        self,
        ranked: List[RankedStrategy],
    ) -> Path:
        path = self.output_dir / "leaderboard.json"

        path.write_text(
            json.dumps(
                [item.to_dict() for item in ranked],
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

        return path

    def export_csv(
        self,
        ranked: List[RankedStrategy],
    ) -> Path:
        path = self.output_dir / "leaderboard.csv"

        fieldnames = [
            "rank",
            "candidate_name",
            "strategy_name",
            "overall_score",
            "performance_score",
            "risk_score",
            "consistency_score",
            "robustness_score",
            "confidence_score",
            "tier",
            "recommendation",
            "cagr",
            "sharpe_ratio",
            "max_drawdown",
            "profit_factor",
            "total_trades",
        ]

        with open(path, "w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()

            for item in ranked:
                metrics = item.metrics

                writer.writerow(
                    {
                        "rank": item.rank,
                        "candidate_name": item.candidate_name,
                        "strategy_name": item.strategy_name,
                        "overall_score": item.breakdown.overall_score,
                        "performance_score": item.breakdown.performance_score,
                        "risk_score": item.breakdown.risk_score,
                        "consistency_score": item.breakdown.consistency_score,
                        "robustness_score": item.breakdown.robustness_score,
                        "confidence_score": item.breakdown.confidence_score,
                        "tier": item.tier,
                        "recommendation": item.recommendation,
                        "cagr": metrics.get("cagr", 0.0),
                        "sharpe_ratio": metrics.get("sharpe_ratio", 0.0),
                        "max_drawdown": metrics.get("max_drawdown", 0.0),
                        "profit_factor": metrics.get("profit_factor", 0.0),
                        "total_trades": metrics.get("total_trades", 0),
                    }
                )

        return path

    def export_summary(
        self,
        ranked: List[RankedStrategy],
    ) -> Path:
        path = self.output_dir / "summary.json"

        tier_counts: Dict[str, int] = {}

        for item in ranked:
            tier_counts[item.tier] = tier_counts.get(item.tier, 0) + 1

        summary: Dict[str, Any] = {
            "total_ranked": len(ranked),
            "top_candidate": (
                ranked[0].to_dict()
                if ranked
                else None
            ),
            "tier_counts": tier_counts,
            "average_overall_score": (
                round(
                    sum(
                        item.breakdown.overall_score
                        for item in ranked
                    ) / len(ranked),
                    4,
                )
                if ranked
                else 0.0
            ),
        }

        path.write_text(
            json.dumps(
                summary,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

        return path
