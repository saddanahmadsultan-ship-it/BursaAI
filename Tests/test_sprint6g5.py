from pathlib import Path
import sys
import tempfile

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Bootstrap.version_manifest import VersionManifest
from Bootstrap.release_manifest import ReleaseManifestWriter
from Bootstrap.backup_manager import ReleaseBackupManager


def main():
    with tempfile.TemporaryDirectory() as folder:
        source = Path(folder) / "source"
        source.mkdir()

        test_file = source / "sample.txt"
        test_file.write_text(
            "BursaAI backup test",
            encoding="utf-8",
        )

        manager = ReleaseBackupManager()

        backup_path = manager.create_backup(
            source,
            Path(folder) / "backups",
        )

        backup = Path(backup_path)

        assert backup.exists()
        assert (backup / "sample.txt").exists()

        restore_target = Path(folder) / "restored"

        restored_path = manager.rollback(
            backup,
            restore_target,
        )

        restored = Path(restored_path)

        assert restored.exists()
        assert (restored / "sample.txt").exists()

        assert (
            (restored / "sample.txt").read_text(
                encoding="utf-8"
            )
            == "BursaAI backup test"
        )

        manifest = VersionManifest(
            modules=[
                "Core",
                "Framework",
                "Adapters",
                "Trading",
                "Notifications",
                "Journal",
                "Analytics",
                "WalkForward",
                "Bootstrap",
            ]
        )

        manifest_path = (
            ReleaseManifestWriter().write(
                manifest,
                Path(folder) / "version_manifest.json",
            )
        )

        manifest_file = Path(manifest_path)

        assert manifest_file.exists()

        content = manifest_file.read_text(
            encoding="utf-8"
        )

        assert '"app_name": "BursaAI"' in content
        assert '"version": "6.0"' in content
        assert '"release": "Sprint 6G.5"' in content

    print("=" * 92)
    print("BURSAAI v6.0 SPRINT 6G.5 FIX 1 TEST")
    print("=" * 92)
    print("Project Root Import       : OK")
    print("Release Backup            : OK")
    print("Backup Verification       : OK")
    print("Rollback                  : OK")
    print("Rollback Verification     : OK")
    print("Version Manifest          : OK")
    print("Manifest JSON Export      : OK")
    print("=" * 92)
    print(
        "SPRINT 6G.5 RELEASE BACKUP, "
        "ROLLBACK & VERSION MANIFEST OK"
    )


if __name__ == "__main__":
    main()
