from pathlib import Path
import sys
import tempfile
from zipfile import ZipFile

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Release.integrity import IntegrityVerifier
from Release.preflight import ReleasePreflight
from Release.rc_builder import ReleaseCandidateBuilder
from Release.release_manifest import RCManifestBuilder


def main():
    with tempfile.TemporaryDirectory() as folder:
        project = Path(folder) / "project"
        project.mkdir()

        for name in (
            "Core",
            "Framework",
            "Adapters",
            "Trading",
            "Notifications",
            "Journal",
            "Analytics",
            "WalkForward",
            "Bootstrap",
            "Config",
            "Tests",
        ):
            path = project / name
            path.mkdir()
            (path / "__init__.py").write_text(
                "",
                encoding="utf-8",
            )

        (project / "main_v6.py").write_text(
            "print('BursaAI')\n",
            encoding="utf-8",
        )
        (project / "VERSION").write_text(
            "6.0.0-rc1\n",
            encoding="utf-8",
        )
        (project / "CHANGELOG.md").write_text(
            "# Changelog\n",
            encoding="utf-8",
        )

        manifest_builder = RCManifestBuilder()
        manifest = manifest_builder.build(project)

        manifest_path = (
            Path(folder) / "manifest.json"
        )
        manifest_builder.write(
            manifest,
            manifest_path,
        )

        integrity = IntegrityVerifier().verify(
            project,
            manifest_path,
        )

        assert integrity.success is True
        assert integrity.checked == len(manifest.files)

        build_result = ReleaseCandidateBuilder().build(
            project,
            Path(folder) / "dist",
        )

        archive = Path(build_result.archive_path)

        assert archive.exists()
        assert Path(build_result.manifest_path).exists()
        assert build_result.files_added > 0

        with ZipFile(archive) as zip_file:
            names = zip_file.namelist()

        assert any(
            name.endswith("/VERSION")
            for name in names
        )
        assert any(
            name.endswith(
                "/Release/version_manifest.json"
            )
            for name in names
        )

    print("=" * 94)
    print("BURSAAI v6.0 SPRINT 6H RC1 TEST")
    print("=" * 94)
    print("Version File              : OK")
    print("RC Manifest Model         : OK")
    print("Manifest Builder          : OK")
    print("SHA256 Integrity          : OK")
    print("RC Archive Builder        : OK")
    print("Archive Structure         : OK")
    print("Manifest Included         : OK")
    print("=" * 94)
    print("SPRINT 6H BURSAAI v6.0.0 RC1 OK")


if __name__ == "__main__":
    main()
