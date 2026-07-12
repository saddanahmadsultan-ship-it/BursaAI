from __future__ import annotations
import unittest
from Tools.repository_cleanup_audit import audit_files

class TestRepositoryCleanupRC0(unittest.TestCase):
    def test_detects_archive_path(self):
        prefix_hits, suffix_hits, large_files = audit_files(["Archive/demo/file.py"])
        self.assertEqual(prefix_hits, ["Archive/demo/file.py"])
        self.assertEqual(suffix_hits, [])
        self.assertEqual(large_files, [])

    def test_detects_executable(self):
        _, suffix_hits, _ = audit_files(["Tools/installer.exe"])
        self.assertEqual(suffix_hits, ["Tools/installer.exe"])

    def test_clean_source_file(self):
        prefix_hits, suffix_hits, large_files = audit_files(["Research/ranking_engine.py"])
        self.assertEqual(prefix_hits, [])
        self.assertEqual(suffix_hits, [])
        self.assertEqual(large_files, [])

if __name__ == "__main__":
    unittest.main(verbosity=2)
