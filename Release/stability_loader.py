from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class StabilityEvidenceLoader:
    def __init__(
        self,
        project_root: str | Path,
    ):
        self.project_root = Path(
            project_root
        ).resolve()

    def _load_json(
        self,
        relative_path: str,
    ) -> Dict[str, Any] | None:
        path = self.project_root / relative_path

        if not path.exists():
            return None

        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    def load_regression(self):
        return self._load_json(
            "Reports/Release/regression_report.json"
        )

    def load_rc_validation(self):
        return self._load_json(
            "Reports/Release/rc1_validation_report.json"
        )

    def load_soak(self):
        return self._load_json(
            "Reports/Release/rc1_paper_soak_report.json"
        )

    def load_manifest(self):
        return self._load_json(
            "Dist/BursaAI_v6.0.0_rc1_manifest.json"
        )

    def load_all(self) -> Dict[str, Any]:
        return {
            "regression": self.load_regression(),
            "validation": self.load_rc_validation(),
            "soak": self.load_soak(),
            "manifest": self.load_manifest(),
        }
