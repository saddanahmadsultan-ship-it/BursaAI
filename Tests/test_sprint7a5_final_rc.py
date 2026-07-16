from __future__ import annotations

import tempfile
import unittest
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


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TestSprint7A5FinalRC(unittest.TestCase):

    def test_unified_pipeline(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)

            for relative in (
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
            ):
                path = root / relative
                path.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )
                path.write_text(
                    "# test",
                    encoding="utf-8",
                )

            pipeline = UnifiedResearchPipeline(
                deterministic_mock_walk_forward,
                UnifiedPipelineConfig(
                    project_root=root,
                    max_candidates=6,
                    max_workers=2,
                ),
            )

            result = pipeline.run()

            self.assertEqual(
                result["status"],
                "COMPLETED",
            )

            self.assertEqual(
                result["failed_candidates"],
                0,
            )

            self.assertEqual(
                result["completed_candidates"],
                6,
            )

            self.assertEqual(
                len(result["leaderboard"]),
                6,
            )

            self.assertEqual(
                len(result["pareto_points"]),
                6,
            )

            self.assertEqual(
                len(result["promotions"]),
                6,
            )

    def test_release_gate_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)

            for relative in (
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
            ):
                path = root / relative
                path.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )
                path.write_text(
                    "# test",
                    encoding="utf-8",
                )

            output = root / "Reports" / "x.json"
            output.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            output.write_text(
                "{}",
                encoding="utf-8",
            )

            result = {
                "status": "COMPLETED",
                "total_candidates": 2,
                "completed_candidates": 2,
                "failed_candidates": 0,
                "leaderboard": [object()],
                "pareto_points": [object()],
                "promotions": [object()],
                "ranking_outputs": {
                    "json": output,
                },
                "pareto_outputs": {},
            }

            gate = ResearchReleaseGate(
                root
            ).evaluate(result)

            self.assertTrue(
                gate["passed"]
            )

    def test_manifest_written(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)

            source = root / "sample.py"
            source.write_text(
                "print('ok')",
                encoding="utf-8",
            )

            manifest = ReleaseManifestV7(
                root
            ).build(["sample.py"])

            self.assertEqual(
                len(manifest["files"]),
                1,
            )

            self.assertTrue(
                Path(
                    manifest["manifest_path"]
                ).exists()
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
