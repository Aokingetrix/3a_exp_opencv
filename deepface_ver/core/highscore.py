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
        "history": [],
        "recent": ["名無し"],
    }

def load() -> Dict[str, Any]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if HIGHSCORE_PATH.exists():
        try:
            with HIGHSCORE_PATH.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            if BACKUP_PATH.exists():
                try:
                    with BACKUP_PATH.open("r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception: pass
            return _default_structure()
    else:
        return _default_structure()

def save(data: Dict[str, Any]) -> None:
    tmp = HIGHSCORE_PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    if HIGHSCORE_PATH.exists():
        HIGHSCORE_PATH.replace(BACKUP_PATH)
    tmp.replace(HIGHSCORE_PATH)

def add_history(name: str, score: int, date: Optional[str] = None) -> None:
    data = load()
    history = data.get("history", [])
    if date is None:
        date = datetime.now().isoformat()
    history.append({"name": name or "名無し", "score": int(score), "date": date})
    data["history"] = history
    save(data)

def update_if_better(name: str, score: int) -> bool:
    best_scores = get_best_for_name(name, n=1)
    is_better = not best_scores or int(score) > int(best_scores[0])
    add_history(name, score)
    return is_better

def get_all_names_best(n: int = 5) -> List[Dict[str, Any]]:
    data = load()
    history = data.get("history", [])
    best_by_name = {}
    for rec in history:
        name = rec.get("name", "名無し")
        score = int(rec.get("score", 0))
        if name not in best_by_name or score > best_by_name[name]:
            best_by_name[name] = score
    items = [{"name": k, "score": v} for k, v in best_by_name.items()]
    items.sort(key=lambda x: x["score"], reverse=True)
    return items[:n]

# --- 新設: 本日のベスト3を取得 ---
def get_todays_best(n: int = 3) -> List[Dict[str, Any]]:
    data = load()
    history = data.get("history", [])
    today = datetime.now().date()
    
    todays_history = []
    for rec in history:
        try:
            rec_date = datetime.fromisoformat(rec.get("date", "")).date()
            if rec_date == today:
                todays_history.append(rec)
        except Exception: continue

    best_by_name = {}
    for rec in todays_history:
        name = rec.get("name", "名無し")
        score = int(rec.get("score", 0))
        if name not in best_by_name or score > best_by_name[name]:
            best_by_name[name] = score
            
    items = [{"name": k, "score": v} for k, v in best_by_name.items()]
    items.sort(key=lambda x: x["score"], reverse=True)
    return items[:n]

# --- 新設: 指定スコアが何位かを取得 ---
def get_rank(score: int, is_today: bool = False) -> int:
    data = load()
    history = data.get("history", [])
    if is_today:
        today = datetime.now().date()
        history = [r for r in history if datetime.fromisoformat(r.get("date", "")).date() == today]
    
    best_scores = {}
    for r in history:
        name = r.get("name", "名無し")
        s = int(r.get("score", 0))
        if name not in best_scores or s > best_scores[name]:
            best_scores[name] = s
            
    rank = 1
    for s in best_scores.values():
        if s > score:
            rank += 1
    return rank

def get_best_for_name(name: str, n: int = 3) -> List[int]:
    data = load()
    history = data.get("history", [])
    scores = [int(rec.get("score", 0)) for rec in history if rec.get("name") == name]
    scores.sort(reverse=True)
    return scores[:n]

def add_recent(name: str) -> None:
    data = load()
    recent = data.get("recent", ["名無し"])
    name = name or "名無し"
    if name in recent: recent.remove(name)
    recent.insert(0, name)
    data["recent"] = recent[:RECENT_MAX]
    save(data)