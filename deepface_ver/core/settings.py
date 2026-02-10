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

BGM_PATHS = {
    "title": "data/sounds/bgm_title.mp3",
    "play": "data/sounds/bgm_play.mp3",
    "finish": "data/sounds/bgm_finish.mp3",
}

SE_PATHS = {
    "select": "data/sounds/se_select.mp3",
    "count": "data/sounds/se_count.mp3",
    "success": "data/sounds/se_success.mp3",
    "fail": "data/sounds/se_fail.mp3",
}
