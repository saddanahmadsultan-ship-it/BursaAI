from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass(slots=True)
class IntegrityResult:
    success: bool
    checked: int = 0
    missing: List[str] = field(default_factory=list)
    mismatched: List[str] = field(default_factory=list)


class IntegrityVerifier:
    @staticmethod
    def sha256(path: Path) -> str:
        digest = hashlib.sha256()

        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)

        return digest.hexdigest()

    def verify(
        self,
        project_root: str | Path,
        manifest_path: str | Path,
    ) -> IntegrityResult:
        root = Path(project_root)
        manifest = json.loads(
            Path(manifest_path).read_text(encoding="utf-8")
        )

        missing = []
        mismatched = []
        checked = 0

        for item in manifest.get("files", []):
            relative = item["path"]
            expected = item["sha256"]
            path = root / relative

            if not path.exists():
                missing.append(relative)
                continue

            checked += 1

            if self.sha256(path) != expected:
                mismatched.append(relative)

        return IntegrityResult(
            success=not missing and not mismatched,
            checked=checked,
            missing=missing,
            mismatched=mismatched,
        )
