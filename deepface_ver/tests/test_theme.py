from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from deepface_ver.core.theme import ThemeError, load_theme

DEFAULT_MANIFEST = Path(__file__).resolve().parents[1] / "data" / "theme.toml"


class ThemeTests(unittest.TestCase):
    def test_default_theme_is_complete(self) -> None:
        theme = load_theme(DEFAULT_MANIFEST)
        self.assertEqual("default", theme.theme_id)
        self.assertEqual(6, len(theme.text_value("instruction_lines", [])))
        self.assertTrue(Path(theme.images["emotion_happy"]).is_file())

    def test_partial_external_theme_falls_back_to_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "background.ppm").write_text("P3\n1 1\n255\n0 0 0\n", encoding="ascii")
            (root / "theme.toml").write_text(
                "\n".join(
                    [
                        "schema_version = 1",
                        'id = "friends"',
                        'display_name = "Friends"',
                        "[text]",
                        'title = "FRIENDS"',
                        "[backgrounds]",
                        'title = "background.ppm"',
                    ]
                ),
                encoding="utf-8",
            )
            theme = load_theme(DEFAULT_MANIFEST, root)
        self.assertEqual("friends", theme.theme_id)
        self.assertEqual("FRIENDS", theme.text["title"])
        self.assertIn("emotion_happy", theme.images)

    def test_referenced_missing_asset_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "theme.toml").write_text(
                'schema_version = 1\nid = "bad"\ndisplay_name = "Bad"\n'
                '[images]\nclock = "missing.png"\n',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ThemeError, "missing.png"):
                load_theme(DEFAULT_MANIFEST, root)


if __name__ == "__main__":
    unittest.main()
