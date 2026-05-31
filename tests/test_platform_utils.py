import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.platform_utils import find_font, open_path


class PlatformUtilsTest(unittest.TestCase):
    def test_open_path_uses_macos_open_command(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch("src.platform_utils.subprocess.run") as run:
                open_path(tmp_dir, platform_name="darwin")

        run.assert_called_once_with(["open", str(Path(tmp_dir).resolve())], check=True)

    def test_open_path_uses_windows_startfile(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with patch("src.platform_utils.os.startfile", create=True) as startfile:
                open_path(tmp_dir, platform_name="win32")

        startfile.assert_called_once_with(str(Path(tmp_dir).resolve()))

    def test_open_path_rejects_missing_target(self):
        with self.assertRaises(FileNotFoundError):
            open_path("missing-path", platform_name="darwin")

    def test_find_font_prefers_environment_setting(self):
        with tempfile.NamedTemporaryFile() as font_file:
            with patch.dict(os.environ, {"AICODING_FONT_PATH": font_file.name}):
                self.assertEqual(font_file.name, find_font())


if __name__ == "__main__":
    unittest.main()
