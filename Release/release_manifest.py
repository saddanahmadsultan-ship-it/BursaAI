from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List
import hashlib
import json


@dataclass(slots=True)
class RCFile:
    path: str
    size_bytes: int
    sha256: str


@dataclass(slots=True)
class RCManifest:
    application: str = "BursaAI"
    version: str = "6.0.0-rc1"
    channel: str = "release-candidate"
    generated_at: str = ""
    files: List[RCFile] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "application": self.application,
            "version": self.version,
            "channel": self.channel,
            "generated_at": self.generated_at,
            "files": [asdict(item) for item in self.files],
            "metadata": dict(self.metadata),
        }


class RCManifestBuilder:
    EXCLUDED_NAMES = {
        "__pycache__",
        ".git",
        ".pytest_cache",
        ".mypy_cache",
        ".idea",
        ".vscode",
    }

    EXCLUDED_SUFFIXES = {
        ".pyc",
        ".pyo",
        ".tmp",
        ".log",
    }

    @staticmethod
    def sha256(path: Path) -> str:
        digest = hashlib.sha256()

        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)

        return digest.hexdigest()

    def _eligible(self, path: Path) -> bool:
        if any(part in self.EXCLUDED_NAMES for part in path.parts):
            return False

        if path.suffix.lower() in self.EXCLUDED_SUFFIXES:
            return False

        return path.is_file()

    def build(
        self,
        project_root: str | Path,
        *,
        metadata: Dict[str, Any] | None = None,
    ) -> RCManifest:
        root = Path(project_root).resolve()

        items = []

        for path in sorted(root.rglob("*")):
            if not self._eligible(path):
                continue

            items.append(
                RCFile(
                    path=str(path.relative_to(root)).replace("\\", "/"),
                    size_bytes=path.stat().st_size,
                    sha256=self.sha256(path),
                )
            )

        return RCManifest(
            generated_at=datetime.now(timezone.utc).isoformat(),
            files=items,
            metadata=dict(metadata or {}),
        )

    def write(
        self,
        manifest: RCManifest,
        output_path: str | Path,
    ) -> str:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                manifest.to_dict(),
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        return str(path)
