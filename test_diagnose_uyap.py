import unittest
from diagnose_uyap import check_java, find_uyap_editor, get_cache_directories, run_diagnostics

class TestUyapDiagnose(unittest.TestCase):
    def test_check_java(self):
        res = check_java()
        self.assertIn("installed", res)

    def test_find_uyap_editor(self):
        res = find_uyap_editor()
        self.assertIn("found", res)

    def test_get_cache_directories(self):
        caches = get_cache_directories()
        self.assertIsInstance(caches, list)
        self.assertGreaterEqual(len(caches), 2)

    def test_run_diagnostics(self):
        diag = run_diagnostics()
        self.assertIn("os", diag)
        self.assertIn("java", diag)
        self.assertIn("editor", diag)
        self.assertIn("recommended_command", diag)

if __name__ == "__main__":
    unittest.main()
