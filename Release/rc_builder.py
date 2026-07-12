from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from Release.release_manifest import RCManifestBuilder


@dataclass(slots=True)
class RCBuildResult:
    archive_path: str
    manifest_path: str
    files_added: int
    size_bytes: int


class ReleaseCandidateBuilder:
    EXCLUDED_NAMES = {
        ".git",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        "Backups",
    }

    EXCLUDED_SUFFIXES = {
        ".pyc",
        ".pyo",
        ".tmp",
        ".log",
    }

    def _eligible(self, path: Path) -> bool:
        if not path.is_file():
            return False

        if any(part in self.EXCLUDED_NAMES for part in path.parts):
            return False

        if path.suffix.lower() in self.EXCLUDED_SUFFIXES:
            return False

        return True

    def build(
        self,
        project_root: str | Path,
        output_directory: str | Path = "Dist",
    ) -> RCBuildResult:
        root = Path(project_root).resolve()
        output = Path(output_directory)
        output.mkdir(parents=True, exist_ok=True)

        manifest_builder = RCManifestBuilder()
        manifest = manifest_builder.build(
            root,
            metadata={
                "release": "BursaAI v6.0.0 RC1",
                "live_trading_approved": False,
            },
        )

        manifest_path = output / "BursaAI_v6.0.0_rc1_manifest.json"
        manifest_builder.write(manifest, manifest_path)

        archive_path = output / "BursaAI_v6.0.0_rc1.zip"
        count = 0

        with ZipFile(archive_path, "w", ZIP_DEFLATED) as archive:
            for path in sorted(root.rglob("*")):
                if not self._eligible(path):
                    continue

                archive.write(
                    path,
                    Path("BursaAI_v6.0.0_rc1")
                    / path.relative_to(root),
                )
                count += 1

            archive.write(
                manifest_path,
                Path("BursaAI_v6.0.0_rc1")
                / "Release"
                / "version_manifest.json",
            )
            count += 1

        return RCBuildResult(
            archive_path=str(archive_path),
            manifest_path=str(manifest_path),
            files_added=count,
            size_bytes=archive_path.stat().st_size,
        )
