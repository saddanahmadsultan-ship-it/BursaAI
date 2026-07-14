from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


class ReleaseManifestV7:
    def __init__(
        self,
        project_root: str | Path,
    ) -> None:
        self.project_root = Path(
            project_root
        )

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()

        with open(path, "rb") as handle:
            for chunk in iter(
                lambda: handle.read(1024 * 1024),
                b"",
            ):
                digest.update(chunk)

        return digest.hexdigest()

    def build(
        self,
        files: Iterable[str],
    ) -> Dict[str, Any]:
        entries: List[Dict[str, Any]] = []

        for relative in files:
            path = self.project_root / relative

            if not path.exists():
                continue

            entries.append(
                {
                    "path": relative.replace("\\", "/"),
                    "size_bytes": path.stat().st_size,
                    "sha256": self._sha256(path),
                }
            )

        manifest = {
            "product": "BursaAI",
            "version": "7.0.0-final-rc",
            "sprint": "7A.5",
            "release": "Final RC",
            "files": entries,
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

        path = output / "release_manifest_v7.json"

        path.write_text(
            json.dumps(
                manifest,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

        manifest["manifest_path"] = str(path)

        return manifest
