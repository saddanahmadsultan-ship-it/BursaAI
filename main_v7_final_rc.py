from __future__ import annotations

from pathlib import Path

from Release.release_manifest_v7 import (
    ReleaseManifestV7,
)
from Release.research_release_gate import (
    ResearchReleaseGate,
)
from Research.mock_walk_forward import (
    deterministic_mock_walk_forward,
)
from Research.unified_pipeline import (
    UnifiedPipelineConfig,
    UnifiedResearchPipeline,
)


PROJECT_ROOT = Path(__file__).resolve().parent


def main() -> int:
    print("=" * 96)
    print(" BursaAI v7 Sprint 7A.5 Final RC — Unified Research Pipeline")
    print("=" * 96)

    pipeline = UnifiedResearchPipeline(
        deterministic_mock_walk_forward,
        UnifiedPipelineConfig(
            project_root=PROJECT_ROOT,
            experiment_name=(
                "Sprint 7A.5 Final RC Validation"
            ),
            symbol="1155.KL",
            max_candidates=12,
            max_workers=4,
            checkpoint_every=2,
            max_retries=1,
        ),
    )

    result = pipeline.run()

    gate = ResearchReleaseGate(
        PROJECT_ROOT
    ).evaluate(result)

    manifest = ReleaseManifestV7(
        PROJECT_ROOT
    ).build(
        [
            "Research/unified_pipeline.py",
            "Research/ranking_engine.py",
            "Research/robustness_engine.py",
            "Research/consistency_engine.py",
            "Research/confidence_engine.py",
            "Research/pareto_engine.py",
            "Research/tier_gate.py",
            "Research/promotion_engine.py",
            "Release/research_release_gate.py",
            "Release/release_manifest_v7.py",
            "main_v7_final_rc.py",
        ]
    )

    print()
    print("UNIFIED PIPELINE RESULT")
    print("-" * 96)
    print("Experiment ID :", result["experiment_id"])
    print("Status        :", result["status"])
    print(
        "Candidates    :",
        f"{result['completed_candidates']}/"
        f"{result['total_candidates']}",
    )
    print(
        "Failed        :",
        result["failed_candidates"],
    )

    top = result.get("top_candidate")

    if top is not None:
        print()
        print("TOP STRATEGY")
        print("-" * 96)
        print("Name          :", top.candidate_name)
        print(
            "AI Score      :",
            f"{top.breakdown.overall_score:.2f}",
        )
        print(
            "Robustness    :",
            f"{top.breakdown.robustness_score:.2f}",
        )
        print(
            "Consistency   :",
            f"{top.breakdown.consistency_score:.2f}",
        )
        print(
            "Confidence    :",
            f"{top.breakdown.confidence_score:.2f}",
        )
        print("Tier          :", top.tier)

    print()
    print("RELEASE GATE")
    print("-" * 96)

    for check in gate["checks"]:
        status = "PASS" if check["passed"] else "FAIL"
        print(
            f"{status:<5} "
            f"{check['name']:<32} "
            f"{check['message']}"
        )

    print()
    print("Gate Report   :", gate["report_path"])
    print("Manifest      :", manifest["manifest_path"])
    print("=" * 96)

    if gate["passed"]:
        print("SPRINT 7A.5 FINAL RC — RELEASE GATE PASSED")
        print("=" * 96)
        return 0

    print("SPRINT 7A.5 FINAL RC — RELEASE GATE FAILED")
    print("=" * 96)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
