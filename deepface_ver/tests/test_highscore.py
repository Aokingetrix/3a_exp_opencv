from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from deepface_ver.core.highscore import HighscoreStore


class HighscoreStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "scores.json"
        self.now = datetime(2026, 8, 29, 12, 0, 0)
        self.store = HighscoreStore(self.path, now=lambda: self.now)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_rankings_and_recent_names(self) -> None:
        self.store.add_history("A", 100)
        self.store.add_history("B", 300)
        self.store.add_history("A", 200)
        self.store.add_recent("A")
        self.assertEqual(
            [{"name": "B", "score": 300}, {"name": "A", "score": 200}],
            self.store.get_all_names_best(),
        )
        self.assertEqual(2, self.store.get_rank(200))
        self.assertEqual("A", self.store.load()["recent"][0])

    def test_corrupt_primary_uses_backup(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("not json", encoding="utf-8")
        self.store.backup_path.write_text(
            json.dumps({"history": [{"name": "A", "score": 10}], "recent": []}),
            encoding="utf-8",
        )
        self.assertEqual("A", self.store.load()["history"][0]["name"])

    def test_atomic_save_leaves_no_temporary_file(self) -> None:
        self.store.save({"history": [], "recent": []})
        self.assertTrue(self.path.exists())
        self.assertFalse(self.path.with_suffix(".json.tmp").exists())


if __name__ == "__main__":
    unittest.main()
