from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from Tools.pre_commit_security_check import scan


class TestGitMigrationPack(unittest.TestCase):

    def test_clean_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "safe.py").write_text(
                "VALUE = 123",
                encoding="utf-8",
            )

            secrets, large_files = scan(root)

            self.assertEqual(secrets, [])
            self.assertEqual(large_files, [])

    def test_detects_private_key(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "bad.txt").write_text(
                "-----BEGIN " + "PRIVATE KEY-----",
                encoding="utf-8",
            )

            secrets, _ = scan(root)

            self.assertEqual(len(secrets), 1)

    def test_detects_token(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "bad.py").write_text(
                'TOKEN = "' + "123456789:" + "A" * 35 + '"',
                encoding="utf-8",
            )

            secrets, _ = scan(root)

            self.assertGreaterEqual(len(secrets), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
