# compatibility shim for settings
from deepface_ver.core.settings import *
__all__ = [
    "WII_BACKGROUND","WII_CHECK","WII_BROWN","WII_BROWN_2","TEXT_DARK",
    "ACCENT_BLUE","ACCENT_GREEN","ACCENT_RED","WII_TRANSLUCENT_BG","WII_SHADOW_COLOR",
    "FONT_PATH","TILE_SIZE","RECOGNITION_HISTORY_SIZE","BGM_PATHS","SE_PATHS"
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

# --- UI設定 ---
TILE_SIZE = 40 # チェック模様の1マスのサイズ
RECOGNITION_HISTORY_SIZE = 3 # 表情認識の平滑化サイズ

# --- サウンドパス ---
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