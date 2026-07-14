from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List


@dataclass
class GateCheck:
    name: str
    passed: bool
    message: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ResearchReleaseGate:
    REQUIRED_FILES = (
        "Research/unified_pipeline.py",
        "Research/ranking_engine.py",
        "Research/robustness_engine.py",
        "Research/consistency_engine.py",
        "Research/confidence_engine.py",
        "Research/pareto_engine.py",
        "Research/tier_gate.py",
        "Research/promotion_engine.py",
        "main_v7_final_rc.py",
        "Tests/test_sprint7a5_final_rc.py",
    )

    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root)

    def evaluate(
        self,
        pipeline_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        checks: List[GateCheck] = []

        checks.append(
            self._check_required_files()
        )

        checks.append(
            GateCheck(
                name="experiment_completed",
                passed=(
                    pipeline_result.get("status")
                    == "COMPLETED"
                ),
                message=(
                    f"Status={pipeline_result.get('status')}"
                ),
            )
        )

        checks.append(
            GateCheck(
                name="zero_failed_candidates",
                passed=(
                    int(
                        pipeline_result.get(
                            "failed_candidates",
                            0,
                        )
                    )
                    == 0
                ),
                message=(
                    "Failed candidates="
                    f"{pipeline_result.get('failed_candidates')}"
                ),
            )
        )

        total = int(
            pipeline_result.get(
                "total_candidates",
                0,
            )
        )

        completed = int(
            pipeline_result.get(
                "completed_candidates",
                0,
            )
        )

        checks.append(
            GateCheck(
                name="all_candidates_completed",
                passed=(
                    total > 0
                    and completed == total
                ),
                message=(
                    f"Completed={completed}/{total}"
                ),
            )
        )

        leaderboard = pipeline_result.get(
            "leaderboard",
            [],
        )

        checks.append(
            GateCheck(
                name="leaderboard_generated",
                passed=bool(leaderboard),
                message=(
                    f"Entries={len(leaderboard)}"
                ),
            )
        )

        pareto_points = pipeline_result.get(
            "pareto_points",
            [],
        )

        checks.append(
            GateCheck(
                name="pareto_generated",
                passed=bool(pareto_points),
                message=(
                    f"Points={len(pareto_points)}"
                ),
            )
        )

        promotions = pipeline_result.get(
            "promotions",
            [],
        )

        checks.append(
            GateCheck(
                name="promotion_decisions_generated",
                passed=bool(promotions),
                message=(
                    f"Decisions={len(promotions)}"
                ),
            )
        )

        output_paths = {
            **pipeline_result.get(
                "ranking_outputs",
                {},
            ),
            **pipeline_result.get(
                "pareto_outputs",
                {},
            ),
        }

        missing_outputs = [
            str(path)
            for path in output_paths.values()
            if not Path(path).exists()
        ]

        checks.append(
            GateCheck(
                name="reports_written",
                passed=(
                    bool(output_paths)
                    and not missing_outputs
                ),
                message=(
                    "Missing="
                    f"{missing_outputs}"
                ),
            )
        )

        passed = all(
            check.passed
            for check in checks
        )

        report = {
            "release": "Sprint 7A.5 Final RC",
            "passed": passed,
            "checks": [
                check.to_dict()
                for check in checks
            ],
        }

        output = (
            self.project_root
            / "Reports"
            / "ReleaseGate"
        )

        output.mkdir(
            parents=True,
            exist_ok=True,
        )

        report_path = (
            output
            / "sprint7a5_final_rc_gate.json"
        )

        report_path.write_text(
            json.dumps(
                report,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

        report["report_path"] = str(
            report_path
        )

        return report

    def _check_required_files(self) -> GateCheck:
        missing = [
            relative
            for relative in self.REQUIRED_FILES
            if not (
                self.project_root
                / relative
            ).exists()
        ]

        return GateCheck(
            name="required_files",
            passed=not missing,
            message=f"Missing={missing}",
        )
