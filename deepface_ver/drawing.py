# compatibility shim for drawing
from deepface_ver.ui.drawing import *
__all__ = ["draw_title_screen", "draw_instruction_screen", "draw_game_background", "draw_round_start_screen", "draw_playing_screen", "draw_result_screen", "draw_finish_screen"]
    
    # --- 2. 背景ボックス付きのタイトルを描画 ---
    
    # --- 2a. フォントとテキストSurfaceを準備 ---
    try:
        font_l = pygame.font.Font(settings.FONT_PATH, 70) # "あまのじゃくゲーム"
        font_m = pygame.font.Font(settings.FONT_PATH, 40) # "[S]スタート!"
    except Exception:
        font_l = pygame.font.Font(None, 74)
        font_m = pygame.font.Font(None, 44)

    title_text_surf = font_l.render("あまのじゃくゲーム", True, settings.TEXT_DARK)
    start_text_surf = font_m.render("[S] スタート!", True, settings.TEXT_DARK)

    # --- 2b. UIボックスのサイズを計算 ---
    padding = 20
    shadow_offset = 5
    
    box_width = max(title_text_surf.get_width(), start_text_surf.get_width()) + (padding * 2)
    box_height = title_text_surf.get_height() + start_text_surf.get_height() + (padding * 3)
    
    # ボックス用のSurfaceを生成 (影を含む)
    box_total_w = box_width + shadow_offset
    box_total_h = box_height + shadow_offset
    box_surf = pygame.Surface((box_total_w, box_total_h), flags=pygame.SRCALPHA)
    box_surf.fill((0, 0, 0, 0)) # 透明
    
    # --- 2c. ボックス（影と本体）を描画 ---
    border_radius = 20 # 角丸の半径
    shadow_rect = pygame.Rect(shadow_offset, shadow_offset, box_width, box_height)
    main_rect = pygame.Rect(0, 0, box_width, box_height)
    
    try:
        # 影
        pygame.draw.rect(box_surf, settings.WII_SHADOW_COLOR, shadow_rect, border_radius=border_radius)
        # 本体
        pygame.draw.rect(box_surf, settings.WII_TRANSLUCENT_BG, main_rect, border_radius=border_radius)
    except TypeError: # Pygame 2.0 未満の場合
        pygame.draw.rect(box_surf, settings.WII_SHADOW_COLOR, shadow_rect)
        pygame.draw.rect(box_surf, settings.WII_TRANSLUCENT_BG, main_rect)


    # --- 2d. テキストをボックス用Surfaceに描画 ---
    
    # "あまのじゃくゲーム" (ボックスの上部中央)
    title_rect = title_text_surf.get_rect(centerx=box_width // 2, top=padding)
    box_surf.blit(title_text_surf, title_rect)
    
    # "[S] スタート!" (ボックスの下部中央)
    start_rect = start_text_surf.get_rect(
        centerx=box_width // 2, 
        top=title_text_surf.get_height() + (padding * 2)
    )
    box_surf.blit(start_text_surf, start_rect)

    # --- 2e. 完成したボックスを画面中央に描画 ---
    box_final_x = (SCREEN_WIDTH - box_total_w) // 2
    box_final_y = (SCREEN_HEIGHT - box_total_h) // 2
    surface.blit(box_surf, (box_final_x, box_final_y))


# ... (draw_title_screen の後) ...

def draw_instruction_screen(surface, background_surface, screen_w, screen_h):
    """
    あそびかた説明画面を描画する (フルスクリーン、キャラ付き)
    """
    
    # --- 1. 背景を描画 ---
    surface.blit(background_surface, (0, 0))

    # --- 2. キャラクターを描画 (右下) ---
    char_w = 200 # キャラ画像の描画サイズ (お好みで調整)
    char_h = 200
    char_x = screen_w - char_w - 30 # 右端から30px内側
    char_y = screen_h - char_h - 30 # 下端から30px内側
    
    try:
        render_image(surface, "data/no_exp.png", char_x, char_y, char_w, char_h, fill_bg=False)
    except Exception as e:
        print(f"キャラ画像エラー: {e}")
        # エラー時は赤い四角
        pygame.draw.rect(surface, (255,0,0), (char_x, char_y, char_w, char_h))

    # --- 3. セリフボックスの準備 ---
    try:
        font_m = pygame.font.Font(settings.FONT_PATH, 20) # 本文
        font_s = pygame.font.Font(settings.FONT_PATH, 35) # 案内
    except Exception:
        font_m = pygame.font.Font(None, 32)
        font_s = pygame.font.Font(None, 39)
    
    # ユーザー指定のセリフ
    lines_text = [
        "こんにちは。わたしは「あまのじゃく」のこども。",
        " 立派な「あまのじゃく」になるため、日々奮闘中。",
        "そこのあなた、「あまのじゃく」の見本を教えてくれない？",
        "わたしの顔（ニコニコ、ムカムカ、シクシク、ビックリ）と、ちがう顔をするの。",
        "「シーン（無感情）」や、「顔が映らない」と、",
        "ライフが減っちゃうから気をつけて！"
    ]

    # --- 4. セリフボックス（影付き角丸）を描画 ---
    
    # 4a. ボックスのサイズと位置を定義 (キャラの左側に配置)
    padding = 20
    shadow_offset = 5
    line_height = 40 # 1行の高さ
    
    box_w = screen_w - char_w - 80 # 画面幅 - キャラ幅 - 隙間
    box_h = (len(lines_text) * line_height) + (padding * 2)
    
    box_x = 30 # 左端から30px
    box_y = (screen_h - box_h) // 2 # 画面の縦中央
    
    # 4b. ボックス用Surfaceを生成 (影を含む)
    box_total_w = box_w + shadow_offset
    box_total_h = box_h + shadow_offset
    box_surf = pygame.Surface((box_total_w, box_total_h), flags=pygame.SRCALPHA)
    
    # 4c. ボックス（影と本体）を描画
    border_radius = 20
    shadow_rect = pygame.Rect(shadow_offset, shadow_offset, box_w, box_h)
    main_rect = pygame.Rect(0, 0, box_w, box_h)
    
    try:
        pygame.draw.rect(box_surf, settings.WII_SHADOW_COLOR, shadow_rect, border_radius=border_radius)
        pygame.draw.rect(box_surf, settings.WII_TRANSLUCENT_BG, main_rect, border_radius=border_radius)
    except TypeError: # フォールバック
        pygame.draw.rect(box_surf, settings.WII_SHADOW_COLOR, shadow_rect)
        pygame.draw.rect(box_surf, settings.WII_TRANSLUCENT_BG, main_rect)
    
    # 4d. セリフをボックス用Surfaceに描画
    y_start = padding
    for i, line in enumerate(lines_text):
        text_surf = font_m.render(line, True, settings.TEXT_DARK)
        # テキストは左揃え (X=padding)
        box_surf.blit(text_surf, (padding, y_start + i * line_height))

    # 4e. 完成したボックスを画面に描画
    surface.blit(box_surf, (box_x, box_y))

    # --- 5. スタート案内 (ボックスの下) ---
    start_surf = font_s.render("[S] スタート！", True, settings.TEXT_DARK)
    start_rect = start_surf.get_rect(centerx=screen_w // 2, top=box_y + box_total_h + 30)
    surface.blit(start_surf, start_rect)

def draw_game_background(surface, background_surface, frame, result, smoothed_emotion, cam_width):
    """ゲーム中（プレイ中、結果表示など）の共通背景を描画する"""
    
    # 背景（チェック模様）を描画
    surface.blit(background_surface, (0, 0))
    
    # カメラ映像を描画
    render_frame(surface, frame, result, cam_width, 0)
    
    # 認識結果のテキストを描画
    draw_text(surface, f"あなた: {smoothed_emotion}", (cam_width + 10, 10))

def draw_round_start_screen(surface, game_manager, cam_width, cam_height):
    """ラウンド開始時の表示 (中央揃え対応)"""
    
    try:
        # 他より一回り大きく表示
        font = pygame.font.Font(settings.FONT_PATH, 80) 
    except Exception:
        font = pygame.font.Font(None, 84)

    # 左パネル（描画エリア）の中心X座標
    panel_center_x = cam_width // 2
    
    # 左パネルの背景を一旦クリア
    surface.fill(settings.WII_BACKGROUND, (0, 0, cam_width, cam_height))

    # --- 2. "ラウンド X" を中央に描画 ---
    text = f"ラウンド {game_manager.current_round}"
    text_surf = font.render(text, True, settings.TEXT_DARK)
    
    # 矩形の中心を、パネルの中心 (X, Y) に設定
    text_rect = text_surf.get_rect(center=(panel_center_x, cam_height // 2))
    
    surface.blit(text_surf, text_rect)

def draw_playing_screen(surface, game_manager, timer_display, cam_width, cam_height):
    """プレイ中のNPCとタイマーを描画する"""
    num_npcs = len(game_manager.npc_emotions)
    base_x, base_y, base_w, base_h = 0, 0, cam_width, cam_height
    
    # 描画エリアを背景色でクリア (render_image の fill_bg=False のため)
    surface.fill(settings.WII_BACKGROUND, (base_x, base_y, base_w, base_h))
    
    if num_npcs == 1:
        npc_emotion = game_manager.npc_emotions[0]
        npc_image_path = game_manager.emotion_images.get(npc_emotion, "")
        render_image(surface, npc_image_path, base_x, base_y, base_w, base_h, fill_bg=False)
    
    elif num_npcs == 2:
        half_w = base_w // 2
        npc_emotion1 = game_manager.npc_emotions[0]
        npc_image_path1 = game_manager.emotion_images.get(npc_emotion1, "")
        render_image(surface, npc_image_path1, base_x, base_y, half_w, base_h, fill_bg=False)
        
        npc_emotion2 = game_manager.npc_emotions[1]
        npc_image_path2 = game_manager.emotion_images.get(npc_emotion2, "")
        render_image(surface, npc_image_path2, base_x + half_w, base_y, half_w, base_h, fill_bg=False)
    
    elif num_npcs >= 3: 
        half_w = base_w // 2
        half_h = base_h // 2
        npc_emotion1 = game_manager.npc_emotions[0]
        npc_image_path1 = game_manager.emotion_images.get(npc_emotion1, "")
        render_image(surface, npc_image_path1, base_x, base_y, half_w, half_h, fill_bg=False)
        
        npc_emotion2 = game_manager.npc_emotions[1]
        npc_image_path2 = game_manager.emotion_images.get(npc_emotion2, "")
        render_image(surface, npc_image_path2, base_x + half_w, base_y, half_w, half_h, fill_bg=False)
        
        npc_emotion3 = game_manager.npc_emotions[2]
        npc_image_path3 = game_manager.emotion_images.get(npc_emotion3, "")
        render_image(surface, npc_image_path3, base_x, base_y + half_h, half_w, half_h, fill_bg=False)
        
        # 4人目がいる場合
        if num_npcs >= 4:
            npc_emotion4 = game_manager.npc_emotions[3]
            npc_image_path4 = game_manager.emotion_images.get(npc_emotion4, "")
            render_image(surface, npc_image_path4, base_x + half_w, base_y + half_h, half_w, half_h, fill_bg=False)

    # タイマーを描画
    timer_display.update(game_manager.timer_sec)
    timer_display.draw()



def draw_result_screen(surface, game_manager, cam_width, cam_height):
    """
    リザルト画面（中央揃え、アイコンVSアイコン表示）を描画する
    """
    
    # --- 1. 準備 (フォントと中心座標) ---
    try:
        font_m = pygame.font.Font(settings.FONT_PATH, 40)
        font_l = pygame.font.Font(settings.FONT_PATH, 70) # For Win/Lose
        font_s = pygame.font.Font(settings.FONT_PATH, 30)
    except Exception:
        font_m = pygame.font.Font(None, 44)
        font_l = pygame.font.Font(None, 74)
        font_s = pygame.font.Font(None, 34)

    # 左パネル（描画エリア）の中心X座標
    panel_center_x = cam_width // 2
    
    # 左パネルの背景を一旦クリア
    surface.fill(settings.WII_BACKGROUND, (0, 0, cam_width, cam_height))

    # --- 2. ラウンド --- (Y=40)
    text_surf = font_m.render(f"ラウンド {game_manager.current_round}", True, settings.TEXT_DARK)
    text_rect = text_surf.get_rect(centerx=panel_center_x, top=40)
    surface.blit(text_surf, text_rect)

    # --- 3. アイコン (相手 vs あなた) --- (Y=120)
    
    # 3a. 「相手」エリア (左半分)
    # (X=0, Y=120, 幅=中心-40, 高さ=200 の矩形エリア)
    npc_area_x = 0
    npc_area_y = 120
    npc_area_w = panel_center_x - 40
    npc_area_h = 200
    
    # 上記エリア内に描画
    num_npcs = len(game_manager.npc_emotions)
    
    if num_npcs == 1:
        npc_img_path = game_manager.emotion_images.get(game_manager.npc_emotions[0], "data/question.png")
        render_image(surface, npc_img_path, npc_area_x, npc_area_y, npc_area_w, npc_area_h, fill_bg=False)
    
    elif num_npcs == 2:
        half_w = npc_area_w // 2
        npc_img_path1 = game_manager.emotion_images.get(game_manager.npc_emotions[0], "data/question.png")
        render_image(surface, npc_img_path1, npc_area_x, npc_area_y, half_w, npc_area_h, fill_bg=False)
        
        npc_img_path2 = game_manager.emotion_images.get(game_manager.npc_emotions[1], "data/question.png")
        render_image(surface, npc_img_path2, npc_area_x + half_w, npc_area_y, half_w, npc_area_h, fill_bg=False)

    elif num_npcs >= 3:
        half_w = npc_area_w // 2
        half_h = npc_area_h // 2
        npc_img_path1 = game_manager.emotion_images.get(game_manager.npc_emotions[0], "data/question.png")
        render_image(surface, npc_img_path1, npc_area_x, npc_area_y, half_w, half_h, fill_bg=False)
        
        npc_img_path2 = game_manager.emotion_images.get(game_manager.npc_emotions[1], "data/question.png")
        render_image(surface, npc_img_path2, npc_area_x + half_w, npc_area_y, half_w, half_h, fill_bg=False)
        
        npc_img_path3 = game_manager.emotion_images.get(game_manager.npc_emotions[2], "data/question.png")
        render_image(surface, npc_img_path3, npc_area_x, npc_area_y + half_h, half_w, half_h, fill_bg=False)
        
        if num_npcs >= 4: # (4人の場合も対応)
            npc_img_path4 = game_manager.emotion_images.get(game_manager.npc_emotions[3], "data/question.png")
            render_image(surface, npc_img_path4, npc_area_x + half_w, npc_area_y + half_h, half_w, half_h, fill_bg=False)

    # 3b. 「あなた」エリア (右半分)
    player_area_x = panel_center_x + 40
    player_area_y = 120
    player_area_w = panel_center_x - 40
    player_area_h = 200
    
    player_img_path = game_manager.emotion_images.get(game_manager.player_emotion, "data/question.png")
    render_image(surface, player_img_path, player_area_x, player_area_y, player_area_w, player_area_h, fill_bg=False)

    # 3c. "VS" テキスト (中央)
    vs_surf = font_m.render("VS", True, settings.TEXT_DARK)
    vs_rect = vs_surf.get_rect(centerx=panel_center_x, centery=npc_area_y + npc_area_h // 2)
    surface.blit(vs_surf, vs_rect)

    # --- 4. Win / Lose テキスト --- (Y=350)
    outcome = game_manager.last_round_outcome
    if outcome == "success":
        result_text = "成功！"
        result_color = settings.ACCENT_GREEN
    else: # fail_match, fail_neutral, fail_missing すべて
        result_text = "失敗..."
        result_color = settings.ACCENT_RED
        
    result_surf = font_l.render(result_text, True, result_color)
    result_rect = result_surf.get_rect(centerx=panel_center_x, top=280)
    surface.blit(result_surf, result_rect)


    # --- 6. 案内 --- (Y=550)
    if game_manager.lives <= 0:
        nav_text = "[S] 最終結果へ"
    else:
        nav_text = "[S] 次のラウンドへ"
        
    nav_surf = font_m.render(nav_text, True, settings.TEXT_DARK)
    nav_rect = nav_surf.get_rect(centerx=panel_center_x, top=380)
    surface.blit(nav_surf, nav_rect)

def draw_finish_screen(surface, background_surface, game_manager, screen_w, screen_h):
    """
    ゲーム終了画面を描画する (キャラ固定、残りスペースを等分)
    """
    
    # --- 1. 背景を描画 ---
    surface.blit(background_surface, (0, 0))

    # --- 2. フォントとSurfaceを「先に」すべて準備 ---
    try:
        font_l = pygame.font.Font(settings.FONT_PATH, 50) # フィニッシュ
        font_m = pygame.font.Font(settings.FONT_PATH, 35) # スコア
        font_s = pygame.font.Font(settings.FONT_PATH, 30) # 案内
    except Exception:
        font_l = pygame.font.Font(None, 54)
        font_m = pygame.font.Font(None, 39)
        font_s = pygame.font.Font(None, 34)

    # ボックス内のセリフ
    lines_surf = [
        font_l.render("フィニッシュ！", True, settings.TEXT_DARK),
        font_m.render(f"スコア: {game_manager.score}", True, settings.ACCENT_BLUE),
        font_s.render("ありがとう！ またあそんでねー", True, settings.TEXT_DARK),
    ]
    
    # 案内テキスト
    nav1_surf = font_s.render("[S] はじめから", True, settings.TEXT_DARK)
    nav2_surf = font_s.render("[R] タイトルにもどる", True, settings.TEXT_DARK)

    # --- 3. 各要素の「幅」と「高さ」を計算 ---
    
    # 3a. ボックス
    padding = 20
    shadow_offset = 5
    line_spacing = 15
    box_w = max(s.get_width() for s in lines_surf) + (padding * 2)
    box_h = sum(s.get_height() for s in lines_surf) + (line_spacing * (len(lines_surf) - 1)) + (padding * 2)
    box_total_w = box_w + shadow_offset
    box_total_h = box_h + shadow_offset

    # 3b. 案内グループ
    nav_spacing = 15
    nav_w = max(nav1_surf.get_width(), nav2_surf.get_width())
    nav_group_height = nav1_surf.get_height() + nav_spacing + nav2_surf.get_height()

    # 3c. キャラクター (固定)
    char_w, char_h = 200, 200
    char_x = screen_w - char_w - 30 # 右端から30px (固定)
    char_y = screen_h - char_h - 30 # 下端から30px (固定)

    # --- 4. X座標（横位置）を計算 (残りスペースを等分) ---
    
    # ボックスと案内が使える「残りの幅」 (左端からキャラの左まで)
    available_width = char_x - 30 # 左右に30pxのマージンを確保
    
    # 2つの要素（ボックス、案内）の合計幅
    content_width = box_total_w + nav_w
    
    # 3つの隙間（左端、中間、右端）のサイズを計算
    try:
        gap_size = (available_width - content_width) / 3
        if gap_size < 10: gap_size = 10
    except ZeroDivisionError:
        gap_size = 10
        
    # 各要素のX座標
    box_x = gap_size
    nav_x = box_x + box_total_w + gap_size
    
    # --- 5. Y座標（縦位置）を計算 (Y中心を揃える) ---

    # 基準となるY中心 (画面の縦中央)
    center_y = screen_h // 2
    
    # 5a. ボックス (縦中央)
    box_y = center_y - (box_total_h // 2)
    
    # 5b. 案内グループ (ボックスのY中心に合わせる)
    nav1_y = center_y - (nav_group_height // 2)
    nav2_y = nav1_y + nav1_surf.get_height() + nav_spacing

    # --- 6. すべての要素を描画 ---
    
    # 6a. ボックス（影付き角丸）
    box_surf = pygame.Surface((box_total_w, box_total_h), flags=pygame.SRCALPHA)
    border_radius = 20
    shadow_rect = pygame.Rect(shadow_offset, shadow_offset, box_w, box_h)
    main_rect = pygame.Rect(0, 0, box_w, box_h)
    try:
        pygame.draw.rect(box_surf, settings.WII_SHADOW_COLOR, shadow_rect, border_radius=border_radius)
        pygame.draw.rect(box_surf, settings.WII_TRANSLUCENT_BG, main_rect, border_radius=border_radius)
    except NameError:
        pygame.draw.rect(box_surf, settings.WII_TRANSLUCENT_BG, main_rect, border_radius=border_radius)
    except TypeError: # フォールバック
        pygame.draw.rect(box_surf, settings.WII_SHADOW_COLOR, shadow_rect)
        pygame.draw.rect(box_surf, settings.WII_TRANSLUCENT_BG, main_rect)
    
    # セリフをボックスに描画 (中央揃え)
    current_y = padding
    for surf in lines_surf:
        rect = surf.get_rect(centerx=box_w // 2, top=current_y)
        box_surf.blit(surf, rect)
        current_y += surf.get_height() + line_spacing
    
    # 完成したボックスを画面に描画
    surface.blit(box_surf, (box_x, box_y))

    # 6b. キャラクター (固定位置)
    try:
        render_image(surface, "data/happy.png", char_x, char_y, char_w, char_h, fill_bg=False)
    except Exception as e:
        pygame.draw.rect(surface, (255,0,0), (char_x, char_y, char_w, char_h))

    # 6c. 案内テキスト (左揃えで配置)
    surface.blit(nav1_surf, (nav_x, nav1_y))
    surface.blit(nav2_surf, (nav_x, nav2_y))

def draw_common_ui(surface, game_manager, cam_w, cam_h, life_display):
    """スコアやライフなど、常に表示するUIを描画する"""
    font_size = 36

    margin_bottom = cam_h - 50
    draw_text(surface, f"スコア: {game_manager.score}", pos = (10, margin_bottom), size = font_size)
    life_label_pos = (cam_w - 300, margin_bottom)
    draw_text(surface, "ライフ", pos = life_label_pos, size = font_size)

    life_display.pos = (cam_w - 180, margin_bottom)
    life_display.draw(game_manager.lives)