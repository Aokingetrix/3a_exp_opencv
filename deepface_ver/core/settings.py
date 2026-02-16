# settings.py moved into core
import pygame
pygame.font.init()

# --- Wii風カラーパレット ---
WII_BACKGROUND = (235, 235, 245)
WII_CHECK = (220, 220, 230)
WII_BROWN = (233, 237, 230)
WII_BROWN_2 = (159, 151, 93)
TEXT_DARK = (79, 85, 84)
ACCENT_BLUE = (0, 150, 255)
ACCENT_GREEN = (0, 200, 100)
ACCENT_RED = (255, 50, 50)
WII_TRANSLUCENT_BG = (245, 245, 255, 250)
WII_SHADOW_COLOR = (0, 0, 0, 80)

import os
import sys
from pathlib import Path

FONT_CANDIDATES = []
if sys.platform.startswith("win"):
    FONT_CANDIDATES = [
        r"C:\\Windows\\Fonts\\Meiryo.ttc",
        r"C:\\Windows\\Fonts\\YuGothic.ttf",
        r"C:\\Windows\\Fonts\\msgothic.ttc",
    ]
else:
    FONT_CANDIDATES = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]

FONT_PATH = None
for p in FONT_CANDIDATES:
    if os.path.exists(p):
        FONT_PATH = p
        break

if FONT_PATH:
    try:
        pygame.font.Font(FONT_PATH, 10)
    except Exception:
        print(f"警告: 指定フォント '{FONT_PATH}' の読み込みに失敗しました。デフォルトフォントを使用します。")
        FONT_PATH = None
else:
    print("警告: 利用可能なフォントが見つかりません。デフォルトフォントを使用します。")

TILE_SIZE = 40
RECOGNITION_HISTORY_SIZE = 3

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PACKAGE_ROOT / "data"


def asset_path(*relative_parts):
    return str(DATA_DIR.joinpath(*relative_parts))

BGM_PATHS = {
    "title": asset_path("sounds", "bgm_title.mp3"),
    "play": asset_path("sounds", "bgm_play.mp3"),
    "finish": asset_path("sounds", "bgm_finish.mp3"),
}

SE_PATHS = {
    "select": asset_path("sounds", "se_select.mp3"),
    "count": asset_path("sounds", "se_count.mp3"),
    "success": asset_path("sounds", "se_success.mp3"),
    "fail": asset_path("sounds", "se_fail.mp3"),
}

CLOCK_IMAGE_PATH = asset_path("clock.png")
HEART_IMAGE_PATH = asset_path("heart.png")
NO_EXP_IMAGE_PATH = asset_path("no_exp.png")
QUESTION_IMAGE_PATH = asset_path("question.png")
EMOTION_IMAGE_PATHS = {
    "ニコニコ": asset_path("happy.png"),
    "シクシク": asset_path("cry.png"),
    "ムカムカ": asset_path("angly.png"),
    "ビックリ": asset_path("surprise.png"),
    "シーン": NO_EXP_IMAGE_PATH,
}
