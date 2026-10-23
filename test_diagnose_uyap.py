import unittest
from unittest.mock import patch
import os
import shutil
import io
import zipfile
from pathlib import Path
from diagnose_uyap import (
    check_java,
    find_uyap_editor,
    get_cache_directories,
    run_diagnostics,
    create_portable_bundle,
    quick_view_udf
)

class TestUyapDiagnose(unittest.TestCase):
    def test_check_java(self):
        res = check_java()
        self.assertIn("installed", res)
        self.assertIn("path", res)

    @patch("subprocess.run")
    @patch("os.path.exists")
    @patch("os.access")
    def test_check_java_fallback(self, mock_access, mock_exists, mock_run):
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

    def test_create_portable_bundle(self):
        temp_dir = Path(__file__).parent / "temp_portable_test"
        try:
            res = create_portable_bundle(temp_dir, memory_mb=2048)
            self.assertEqual(res["memory_mb"], 2048)
            self.assertTrue((temp_dir / "jre").is_dir())
            self.assertTrue((temp_dir / "uyap").is_dir())
            self.assertTrue((temp_dir / "run-uyap.bat").is_file())
            self.assertTrue((temp_dir / "run-uyap.sh").is_file())
            self.assertTrue((temp_dir / "run-uyap.ps1").is_file())
            self.assertTrue((temp_dir / "portable_config.json").is_file())

            # Verify memory limit was injected in bat script
            with open(temp_dir / "run-uyap.bat", "r", encoding="utf-8") as f:
                bat_text = f.read()
                self.assertIn("-Xmx2048m", bat_text)
                self.assertIn("editor.jar", bat_text)
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

    def test_quick_view_udf(self):
        temp_udf = Path(__file__).parent / "temp_view_test.udf"
        sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <template>
          <elements>
            <paragraph><content>ANKARA 4. ASLİYE TİCARET MAHKEMESİNE</content></paragraph>
            <paragraph><content>ESAS NO : 2026/894</content></paragraph>
            <paragraph><content>Dava dilekçesinin özeti burada yer almaktadır.</content></paragraph>
          </elements>
        </template>"""

        try:
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("content.xml", sample_xml.encode("utf-8"))

            with open(temp_udf, "wb") as f:
                f.write(buf.getvalue())

            view_res = quick_view_udf(temp_udf)
            self.assertEqual(view_res["file_name"], "temp_view_test.udf")
            self.assertIn("ANKARA 4. ASLİYE TİCARET MAHKEMESİNE", view_res["court"])
            self.assertEqual(view_res["case_number"], "2026/894")
            self.assertIn("Dava dilekçesinin özeti", view_res["text"])
        finally:
            if temp_udf.exists():
                temp_udf.unlink()

if __name__ == "__main__":
    unittest.main()
