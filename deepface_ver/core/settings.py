# settings.py moved into core
import os
import sys
from pathlib import Path

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
UI_PANEL_BG = (238, 246, 255, 245)
UI_LABEL_BG = (248, 250, 255, 235)

FONT_CANDIDATES = []
if sys.platform.startswith("win"):
    FONT_CANDIDATES = [
        r"C:\Windows\Fonts\Meiryo.ttc",
        r"C:\Windows\Fonts\YuGothic.ttf",
        r"C:\Windows\Fonts\msgothic.ttc",
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

if not FONT_PATH:
    print("警告: 利用可能なフォントが見つかりません。デフォルトフォントを使用します。")

# === システム定数（絶対に削除しない） ===
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
HUMAN_HAPPY_PATH = asset_path("human_faces", "happy_human.png")
HUMAN_CRY_PATH = asset_path("human_faces", "sad_human.png")
HUMAN_ANGRY_PATH = asset_path("human_faces", "angry_human.png")
HUMAN_SURPRISE_PATH = asset_path("human_faces", "surprise_human.png")
HUMAN_NO_EXP_PATH = asset_path("human_faces", "no_exp_human.png")
HUMAN_FACE_IMAGE_PATH = HUMAN_NO_EXP_PATH
EMOTION_IMAGE_PATHS = {
    "ニコニコ": asset_path("happy.png"),
    "シクシク": asset_path("cry.png"),
    "ムカムカ": asset_path("angly.png"),
    "ビックリ": asset_path("surprise.png"),
    "シーン": NO_EXP_IMAGE_PATH,
}

# === 追加機能: 動的フォント＆スタイル管理 ===

# Settings Spine Font 用のパス（存在しなければ通常のフォントにフォールバック）
SPINE_FONT_PATH = asset_path("fonts", "spine_font.ttf") 
if not os.path.exists(SPINE_FONT_PATH):
    SPINE_FONT_PATH = FONT_PATH

def get_font(size: int, use_spine_font: bool = False):
    """
    フォントオブジェクトを安全に取得する一元管理関数。
    drawing.py などの描画側は、直接 pygame.font.Font を呼ばずこれを使う。
    """
    import pygame

    if not pygame.font.get_init():
        pygame.font.init()
    path = SPINE_FONT_PATH if use_spine_font else FONT_PATH
    try:
        return pygame.font.Font(path, size)
    except Exception:
        # フォント読み込みに失敗した場合はデフォルトフォントで少し大きめに
        return pygame.font.Font(None, size + 4)

def get_score_style(score: int):
    """
    スコア到達度に応じた色と、特殊フォント（Spine Font）を使用するかを返す。
    閾値: 100, 500, 1000, 2000, 3000
    """
    if score >= 3000:
        return (255, 215, 0), True      # ゴールド + 特殊フォント
    elif score >= 2000:
        return (148, 0, 211), True      # ダークバイオレット + 特殊フォント
    elif score >= 1000:
        return (255, 50, 50), True      # レッド + 特殊フォント
    elif score >= 500:
        return (255, 140, 0), False     # ダークオレンジ + 通常フォント
    elif score >= 100:
        return (218, 165, 32), False    # ゴールデンロッド + 通常フォント
        
    return TEXT_DARK, False             # 初期状態
