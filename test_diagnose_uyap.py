import unittest
from unittest.mock import patch
import os
import platform
from diagnose_uyap import check_java, find_uyap_editor, get_cache_directories, run_diagnostics

class TestUyapDiagnose(unittest.TestCase):
    def test_check_java(self):
        res = check_java()
        self.assertIn("installed", res)
        self.assertIn("path", res)

    @patch("subprocess.run")
    @patch("os.path.exists")
    @patch("os.access")
    def test_check_java_fallback(self, mock_access, mock_exists, mock_run):
        # First call fails (standard PATH java), second succeeds for homebrew path
        mock_exists.side_effect = lambda path: path == "/opt/homebrew/opt/openjdk@8/bin/java"
        mock_access.return_value = True

        def fake_run(cmd, **kwargs):
            if cmd == ["java", "-version"]:
                raise FileNotFoundError("java not in PATH")
            mock_res = unittest.mock.MagicMock()
            mock_res.stderr = "openjdk version \"1.8.0_392\"\nOpenJDK Runtime"
            mock_res.stdout = ""
            return mock_res

        mock_run.side_effect = fake_run
        res = check_java()
        self.assertTrue(res["installed"])
        self.assertEqual(res["path"], "/opt/homebrew/opt/openjdk@8/bin/java")
        self.assertIn("1.8.0_392", res["version_string"])

    def test_find_uyap_editor(self):
        res = find_uyap_editor()
        self.assertIn("found", res)

    @patch("platform.system", return_value="Darwin")
    @patch("os.path.exists")
    def test_find_uyap_editor_darwin_candidate(self, mock_exists, mock_system):
        mock_exists.side_effect = lambda path: path == "/Applications/UYAP Editor.app"
        res = find_uyap_editor()
        self.assertTrue(res["found"])
        self.assertEqual(res["path"], "/Applications/UYAP Editor.app")

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

