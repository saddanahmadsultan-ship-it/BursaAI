from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List

from Research.pareto_models import ParetoPoint


class ParetoReportExporter:
    def __init__(
        self,
        output_dir: str | Path = "Reports/Pareto",
    ) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def export(
        self,
        points: Iterable[ParetoPoint],
        promotions: List[Dict],
    ) -> Dict[str, Path]:
        points = list(points)

        json_path = self.output_dir / "pareto_front.json"
        csv_path = self.output_dir / "pareto_front.csv"
        promotion_path = self.output_dir / "promotion_report.json"

        json_path.write_text(
            json.dumps(
                [point.to_dict() for point in points],
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

        with open(
            csv_path,
            "w",
            newline="",
            encoding="utf-8-sig",
        ) as handle:
            fieldnames = [
                "candidate_id",
                "result_id",
                "front",
                "domination_count",
                "dominates_count",
                "crowding_distance",
            ]

            writer = csv.DictWriter(
                handle,
                fieldnames=fieldnames,
            )

            writer.writeheader()

            for point in points:
                writer.writerow(
                    {
                        "candidate_id": point.candidate_id,
                        "result_id": point.result_id,
                        "front": point.front,
                        "domination_count": point.domination_count,
                        "dominates_count": point.dominates_count,
                        "crowding_distance": point.crowding_distance,
                    }
                )

        promotion_path.write_text(
            json.dumps(
                promotions,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

        return {
            "pareto_json": json_path,
            "pareto_csv": csv_path,
            "promotion_json": promotion_path,
        }
