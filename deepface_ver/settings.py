# settings.py
import pygame

# pygame.font を初期化 (settings.py が main より先に呼ばれる場合に備える)
pygame.font.init() 

# --- Wii風カラーパレット ---
WII_BACKGROUND = (235, 235, 245) # ごく薄いクールなグレー (背景色)
WII_CHECK = (220, 220, 230) # ごく薄いクールなグレー (背景色)
WII_BROWN = (233, 237, 230) #薄い茶色
WII_BROWN_2 = (159, 151, 93) #とても暗い
TEXT_DARK = (79, 85, 84)       # 濃いグレー (基本の文字色)
ACCENT_BLUE = (0, 150, 255)    # Wiiのボタンのような明るい青 (アクセント)
ACCENT_GREEN = (0, 200, 100)   # 成功時の色
ACCENT_RED = (255, 50, 50)     # 失敗・警告時の色
WII_TRANSLUCENT_BG = (245, 245, 255, 250) #半透明の白
WII_SHADOW_COLOR = (0, 0, 0, 80) # 透明度

# --- パス ---
FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
try:
    # フォントが存在するかテスト
    pygame.font.Font(FONT_PATH, 10)
except (IOError, pygame.error):
    print(f"警告: 指定フォント '{FONT_PATH}' が見つかりません。デフォルトフォントを使用します。")
    FONT_PATH = None # None を指定すると pygame.font.Font がデフォルトフォントを使用する

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