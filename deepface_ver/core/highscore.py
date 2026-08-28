"""High-score persistence with injectable paths and clock."""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

RECENT_MAX = 10
LEGACY_DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def _default_structure() -> dict[str, Any]:
    return {"history": [], "recent": ["名無し"]}


class HighscoreStore:
    def __init__(
        self,
        path: Path,
        *,
        backup_path: Path | None = None,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self.path = Path(path)
        self.backup_path = backup_path or self.path.with_suffix(self.path.suffix + ".bak")
        self._now = now or datetime.now

    def load(self) -> dict[str, Any]:
        for candidate in (self.path, self.backup_path):
            if not candidate.exists():
                continue
            try:
                with candidate.open("r", encoding="utf-8") as stream:
                    value = json.load(stream)
                if isinstance(value, dict):
                    return value
            except (OSError, json.JSONDecodeError, TypeError):
                continue
        return _default_structure()

    def save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        with temporary.open("w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=4)
            stream.flush()
        if self.path.exists():
            self.path.replace(self.backup_path)
        temporary.replace(self.path)

    def add_history(self, name: str, score: int, date: str | None = None) -> None:
        data = self.load()
        history = list(data.get("history", []))
        history.append(
            {
                "name": name or "名無し",
                "score": int(score),
                "date": date or self._now().isoformat(),
            }
        )
        data["history"] = history
        self.save(data)

    def update_if_better(self, name: str, score: int) -> bool:
        best_scores = self.get_best_for_name(name, n=1)
        is_better = not best_scores or int(score) > best_scores[0]
        self.add_history(name, score)
        return is_better

    def get_all_names_best(self, n: int = 5) -> list[dict[str, Any]]:
        return self._best_by_name(self.load().get("history", []))[:n]

    def get_todays_best(self, n: int = 3) -> list[dict[str, Any]]:
        today = self._now().date()
        records = []
        for record in self.load().get("history", []):
            try:
                if datetime.fromisoformat(str(record.get("date", ""))).date() == today:
                    records.append(record)
            except ValueError:
                continue
        return self._best_by_name(records)[:n]

    def get_rank(self, score: int, *, is_today: bool = False) -> int:
        records = self.load().get("history", [])
        if is_today:
            today = self._now().date()
            filtered = []
            for record in records:
                try:
                    if datetime.fromisoformat(str(record.get("date", ""))).date() == today:
                        filtered.append(record)
                except ValueError:
                    continue
            records = filtered
        return 1 + sum(item["score"] > score for item in self._best_by_name(records))

    def get_best_for_name(self, name: str, n: int = 3) -> list[int]:
        scores = [
            int(record.get("score", 0))
            for record in self.load().get("history", [])
            if record.get("name") == name
        ]
        return sorted(scores, reverse=True)[:n]

    def add_recent(self, name: str) -> None:
        data = self.load()
        recent = list(data.get("recent", ["名無し"]))
        normalized = name or "名無し"
        if normalized in recent:
            recent.remove(normalized)
        recent.insert(0, normalized)
        data["recent"] = recent[:RECENT_MAX]
        self.save(data)

    @staticmethod
    def _best_by_name(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        best: dict[str, int] = {}
        for record in records:
            name = str(record.get("name", "名無し"))
            score = int(record.get("score", 0))
            best[name] = max(score, best.get(name, score))
        return sorted(
            ({"name": name, "score": score} for name, score in best.items()),
            key=lambda item: item["score"],
            reverse=True,
        )


_default_store = HighscoreStore(
    LEGACY_DATA_DIR / "highscore.json",
    backup_path=LEGACY_DATA_DIR / "highscore.json.bak",
)


def configure(store: HighscoreStore) -> None:
    global _default_store
    _default_store = store


def load() -> dict[str, Any]:
    return _default_store.load()


def save(data: dict[str, Any]) -> None:
    _default_store.save(data)


def add_history(name: str, score: int, date: str | None = None) -> None:
    _default_store.add_history(name, score, date)


def update_if_better(name: str, score: int) -> bool:
    return _default_store.update_if_better(name, score)


def get_all_names_best(n: int = 5) -> list[dict[str, Any]]:
    return _default_store.get_all_names_best(n)


def get_todays_best(n: int = 3) -> list[dict[str, Any]]:
    return _default_store.get_todays_best(n)


def get_rank(score: int, is_today: bool = False) -> int:
    return _default_store.get_rank(score, is_today=is_today)


def get_best_for_name(name: str, n: int = 3) -> list[int]:
    return _default_store.get_best_for_name(name, n)


def add_recent(name: str) -> None:
    _default_store.add_recent(name)
