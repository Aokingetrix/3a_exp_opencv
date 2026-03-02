from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
HIGHSCORE_PATH = DATA_DIR / "highscore.json"
BACKUP_PATH = DATA_DIR / "highscore.json.bak"
RECENT_MAX = 10


def _default_structure() -> Dict[str, Any]:
    return {
        "history": [],  # list of {name, score, date}
        "recent": ["名無し"],
    }


def load() -> Dict[str, Any]:
    """Load highscore JSON, with fallback to backup and default.

    Returns a dict with keys: 'history' (list) and 'recent' (list).
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if HIGHSCORE_PATH.exists():
        try:
            with HIGHSCORE_PATH.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            # try backup
            if BACKUP_PATH.exists():
                try:
                    with BACKUP_PATH.open("r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception:
                    pass
            return _default_structure()
    else:
        return _default_structure()


def _atomic_save(data: Dict[str, Any]) -> None:
    tmp = HIGHSCORE_PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    # backup current
    try:
        if HIGHSCORE_PATH.exists():
            HIGHSCORE_PATH.replace(BACKUP_PATH)
    except Exception:
        # ignore backup failure
        pass
    tmp.replace(HIGHSCORE_PATH)


def save(data: Dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    _atomic_save(data)


def get_all_names_best(n: int = 10) -> List[Dict[str, Any]]:
    """Return top-n best scores across all names.

    Returns list of {name, score} sorted desc.
    """
    data = load()
    history = data.get("history", [])
    best_by_name: Dict[str, int] = {}
    for rec in history:
        name = rec.get("name", "名無し")
        score = int(rec.get("score", 0))
        if name not in best_by_name or score > best_by_name[name]:
            best_by_name[name] = score
    items = [{"name": k, "score": v} for k, v in best_by_name.items()]
    items.sort(key=lambda x: x["score"], reverse=True)
    return items[:n]


def get_best_for_name(name: str, n: int = 3) -> List[int]:
    data = load()
    history = data.get("history", [])
    scores = [int(rec.get("score", 0)) for rec in history if rec.get("name") == name]
    scores.sort(reverse=True)
    return scores[:n]


def add_recent(name: str) -> None:
    data = load()
    recent: List[str] = data.get("recent", []) or []
    name = name or "名無し"
    if name in recent:
        recent.remove(name)
    recent.insert(0, name)
    recent = recent[:RECENT_MAX]
    data["recent"] = recent
    save(data)


def add_history(name: str, score: int, date: Optional[str] = None) -> None:
    data = load()
    history: List[Dict[str, Any]] = data.get("history", [])
    if date is None:
        date = datetime.utcnow().isoformat()
    history.append({"name": name or "名無し", "score": int(score), "date": date})
    data["history"] = history
    add_recent(name)
    save(data)


def update_if_better(name: str, score: int) -> bool:
    """Add to history and return True if this score is a new personal best for name."""
    bests = get_best_for_name(name, n=1)
    is_better = False
    if not bests or score > bests[0]:
        is_better = True
    add_history(name, int(score))
    return is_better
