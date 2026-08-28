"""Cross-platform runtime options and user-data locations."""

from __future__ import annotations

import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

LOGICAL_WIDTH = 1280
LOGICAL_HEIGHT = 480
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
APP_DIRECTORY = "amanojaku-game"


@dataclass(frozen=True)
class RuntimeOptions:
    camera_index: int = 0
    camera_backend: str = "auto"
    window_size: tuple[int, int] = (LOGICAL_WIDTH, LOGICAL_HEIGHT)
    theme_dir: Path | None = None


def parse_size(value: str) -> tuple[int, int]:
    try:
        width_text, height_text = value.lower().split("x", 1)
        width, height = int(width_text), int(height_text)
    except (TypeError, ValueError) as error:
        raise ValueError("画面サイズは WIDTHxHEIGHT 形式で指定してください") from error
    if width < 320 or height < 240:
        raise ValueError("画面サイズは320x240以上にしてください")
    return width, height


def user_data_root() -> Path:
    if sys.platform.startswith("win"):
        base = os.environ.get("LOCALAPPDATA")
        return Path(base) / APP_DIRECTORY if base else Path.home() / "AppData" / "Local" / APP_DIRECTORY
    base = os.environ.get("XDG_DATA_HOME")
    return Path(base) / APP_DIRECTORY if base else Path.home() / ".local" / "share" / APP_DIRECTORY


def theme_data_dir(theme_id: str) -> Path:
    safe_id = "".join(character for character in theme_id if character.isalnum() or character in "-_")
    if not safe_id:
        raise ValueError("テーマIDには英数字、ハイフン、アンダースコアを使用してください")
    return user_data_root() / "themes" / safe_id


def configure_highscores(theme_id: str, legacy_path: Path | None = None):
    from . import highscore

    destination = theme_data_dir(theme_id) / "highscore.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists() and legacy_path and legacy_path.exists():
        shutil.copy2(legacy_path, destination)
    store = highscore.HighscoreStore(destination)
    highscore.configure(store)
    return store
