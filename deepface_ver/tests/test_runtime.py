from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from deepface_ver.core import highscore
from deepface_ver.core.runtime import configure_highscores, parse_size, theme_data_dir


class RuntimeTests(unittest.TestCase):
    def test_parse_size(self) -> None:
        self.assertEqual((1920, 1080), parse_size("1920x1080"))
        with self.assertRaises(ValueError):
            parse_size("tiny")

    def test_theme_data_directory_is_separated(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            with patch.dict(os.environ, {"LOCALAPPDATA": temp}, clear=False):
                with patch("sys.platform", "win32"):
                    default = theme_data_dir("default")
                    fan = theme_data_dir("fanmade")
            self.assertNotEqual(default, fan)

    def test_legacy_scores_are_migrated_once(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            legacy = temp_path / "legacy.json"
            legacy.write_text('{"history": [], "recent": ["A"]}', encoding="utf-8")
            with patch.dict(os.environ, {"LOCALAPPDATA": str(temp_path / "local")}, clear=False):
                with patch("sys.platform", "win32"):
                    store = configure_highscores("default", legacy)
            self.assertEqual(["A"], store.load()["recent"])
            legacy.write_text('{"history": [], "recent": ["B"]}', encoding="utf-8")
            self.assertEqual(["A"], store.load()["recent"])
            highscore.configure(store)


if __name__ == "__main__":
    unittest.main()
