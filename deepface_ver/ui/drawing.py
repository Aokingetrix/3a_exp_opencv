import pygame
from ..core.utils import draw_text, render_image, render_frame
from .ui_elements import LifeDisplay
from ..core import settings
from ..core.game_manager import GameState


def draw_title_screen(surface, background_surface, floating_images):
    """タイトル画面を描画する"""
    surface.blit(background_surface, (0, 0))
    # --- 1. 浮遊画像を更新・描画 (背景) ---
    for img in floating_images:
        img.update()
        img.draw(surface)

    SCREEN_WIDTH = surface.get_width()
    SCREEN_HEIGHT = surface.get_height()

    # --- 2. 背景ボックス付きのタイトルを描画 ---
    try:
        font_l = pygame.font.Font(settings.FONT_PATH, 70) # "あまのじゃくゲーム"
        font_m = pygame.font.Font(settings.FONT_PATH, 40) # "[S]スタート!"
    except Exception:
        font_l = pygame.font.Font(None, 74)
        font_m = pygame.font.Font(None, 44)

    title_text_surf = font_l.render("あまのじゃくゲーム", True, settings.TEXT_DARK)
    start_text_surf = font_m.render("[S] スタート!", True, settings.TEXT_DARK)

    padding = 20
    shadow_offset = 5

    box_width = max(title_text_surf.get_width(), start_text_surf.get_width()) + (padding * 2)
    box_height = title_text_surf.get_height() + start_text_surf.get_height() + (padding * 3)

    box_total_w = box_width + shadow_offset
    box_total_h = box_height + shadow_offset
    box_surf = pygame.Surface((box_total_w, box_total_h), flags=pygame.SRCALPHA)
    box_surf.fill((0, 0, 0, 0))

    border_radius = 20
    shadow_rect = pygame.Rect(shadow_offset, shadow_offset, box_width, box_height)
    main_rect = pygame.Rect(0, 0, box_width, box_height)

    try:
        pygame.draw.rect(box_surf, settings.WII_SHADOW_COLOR, shadow_rect, border_radius=border_radius)
        pygame.draw.rect(box_surf, settings.WII_TRANSLUCENT_BG, main_rect, border_radius=border_radius)
    except TypeError:
        pygame.draw.rect(box_surf, settings.WII_SHADOW_COLOR, shadow_rect)
        pygame.draw.rect(box_surf, settings.WII_TRANSLUCENT_BG, main_rect)

    title_rect = title_text_surf.get_rect(centerx=box_width // 2, top=padding)
    box_surf.blit(title_text_surf, title_rect)

    start_rect = start_text_surf.get_rect(
        centerx=box_width // 2, 
        top=title_text_surf.get_height() + (padding * 2)
    )
    box_surf.blit(start_text_surf, start_rect)

    box_final_x = (SCREEN_WIDTH - box_total_w) // 2
    box_final_y = (SCREEN_HEIGHT - box_total_h) // 2
    surface.blit(box_surf, (box_final_x, box_final_y))


def draw_instruction_screen(surface, background_surface, screen_w, screen_h):
    """
    あそびかた説明画面を描画する (フルスクリーン、キャラ付き)
    """
    surface.blit(background_surface, (0, 0))

    char_w = 200
    char_h = 200
    char_x = screen_w - char_w - 30
    char_y = screen_h - char_h - 30

    try:
        render_image(surface, "data/no_exp.png", char_x, char_y, char_w, char_h, fill_bg=False)
    except Exception as e:
        print(f"キャラ画像エラー: {e}")
        pygame.draw.rect(surface, (255,0,0), (char_x, char_y, char_w, char_h))

    try:
        font_m = pygame.font.Font(settings.FONT_PATH, 20)
        font_s = pygame.font.Font(settings.FONT_PATH, 35)
    except Exception:
        font_m = pygame.font.Font(None, 32)
        font_s = pygame.font.Font(None, 39)

    lines_text = [
        "こんにちは。わたしは「あまのじゃく」のこども。",
        " 立派な「あまのじゃく」になるため、日々奮闘中。",
        "そこのあなた、「あまのじゃく」の見本を教えてくれない？",
        "わたしの顔（ニコニコ、ムカムカ、シクシク、ビックリ）と、ちがう顔をするの。",
        "「シーン（無感情）」や、「顔が映らない」と、",
        "ライフが減っちゃうから気をつけて！"
    ]

    padding = 20
    shadow_offset = 5
    line_height = 40

    box_w = screen_w - char_w - 80
    box_h = (len(lines_text) * line_height) + (padding * 2)

    box_x = 30
    box_y = (screen_h - box_h) // 2

    box_total_w = box_w + shadow_offset
    box_total_h = box_h + shadow_offset
    box_surf = pygame.Surface((box_total_w, box_total_h), flags=pygame.SRCALPHA)

    border_radius = 20
    shadow_rect = pygame.Rect(shadow_offset, shadow_offset, box_w, box_h)
    main_rect = pygame.Rect(0, 0, box_w, box_h)

    try:
        pygame.draw.rect(box_surf, settings.WII_SHADOW_COLOR, shadow_rect, border_radius=border_radius)
        pygame.draw.rect(box_surf, settings.WII_TRANSLUCENT_BG, main_rect, border_radius=border_radius)
    except TypeError:
        pygame.draw.rect(box_surf, settings.WII_SHADOW_COLOR, shadow_rect)
        pygame.draw.rect(box_surf, settings.WII_TRANSLUCENT_BG, main_rect)

    y_start = padding
    for i, line in enumerate(lines_text):
        text_surf = font_m.render(line, True, settings.TEXT_DARK)
        box_surf.blit(text_surf, (padding, y_start + i * line_height))

    surface.blit(box_surf, (box_x, box_y))

    start_surf = font_s.render("[S] スタート！", True, settings.TEXT_DARK)
    start_rect = start_surf.get_rect(centerx=screen_w // 2, top=box_y + box_total_h + 30)
    surface.blit(start_surf, start_rect)


def draw_game_background(surface, background_surface, frame, result, smoothed_emotion, cam_width):
    surface.blit(background_surface, (0, 0))
    render_frame(surface, frame, result, cam_width, 0)
    draw_text(surface, f"あなた: {smoothed_emotion}", (cam_width + 10, 10))


def draw_round_start_screen(surface, game_manager, cam_width, cam_height):
    try:
        font = pygame.font.Font(settings.FONT_PATH, 80)
    except Exception:
        font = pygame.font.Font(None, 84)

    panel_center_x = cam_width // 2
    surface.fill(settings.WII_BACKGROUND, (0, 0, cam_width, cam_height))

    text = f"ラウンド {game_manager.current_round}"
    text_surf = font.render(text, True, settings.TEXT_DARK)
    text_rect = text_surf.get_rect(center=(panel_center_x, cam_height // 2))
    surface.blit(text_surf, text_rect)


def draw_playing_screen(surface, game_manager, timer_display, cam_width, cam_height):
    num_npcs = len(game_manager.npc_emotions)
    base_x, base_y, base_w, base_h = 0, 0, cam_width, cam_height
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
        
        if num_npcs >= 4:
            npc_emotion4 = game_manager.npc_emotions[3]
            npc_image_path4 = game_manager.emotion_images.get(npc_emotion4, "")
            render_image(surface, npc_image_path4, base_x + half_w, base_y + half_h, half_w, half_h, fill_bg=False)

    timer_display.update(game_manager.timer_sec)
    timer_display.draw()


def draw_result_screen(surface, game_manager, cam_width, cam_height):
    try:
        font_m = pygame.font.Font(settings.FONT_PATH, 40)
        font_l = pygame.font.Font(settings.FONT_PATH, 70)
        font_s = pygame.font.Font(settings.FONT_PATH, 30)
    except Exception:
        font_m = pygame.font.Font(None, 44)
        font_l = pygame.font.Font(None, 74)
        font_s = pygame.font.Font(None, 34)

    panel_center_x = cam_width // 2
    surface.fill(settings.WII_BACKGROUND, (0, 0, cam_width, cam_height))

    text_surf = font_m.render(f"ラウンド {game_manager.current_round}", True, settings.TEXT_DARK)
    text_rect = text_surf.get_rect(centerx=panel_center_x, top=40)
    surface.blit(text_surf, text_rect)

    npc_area_x = 0
    npc_area_y = 120
    npc_area_w = panel_center_x - 40
    npc_area_h = 200

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


def draw_finish_screen(surface, background_surface, game_manager, screen_w, screen_h):
    """ゲーム終了画面を描画する"""
    surface.blit(background_surface, (0, 0))

    try:
        font_l = pygame.font.Font(settings.FONT_PATH, 80)
        font_m = pygame.font.Font(settings.FONT_PATH, 40)
    except Exception:
        font_l = pygame.font.Font(None, 84)
        font_m = pygame.font.Font(None, 44)

    title = "ゲーム終了"
    score_text = f"スコア: {game_manager.score}"
    restart_text = "[R] タイトルへ戻る  /  [S] もう一度遊ぶ"

    title_surf = font_l.render(title, True, settings.TEXT_DARK)
    score_surf = font_m.render(score_text, True, settings.TEXT_DARK)
    restart_surf = font_m.render(restart_text, True, settings.TEXT_DARK)

    cx = screen_w // 2
    surface.blit(title_surf, title_surf.get_rect(center=(cx, screen_h // 2 - 80)))
    surface.blit(score_surf, score_surf.get_rect(center=(cx, screen_h // 2)))
    surface.blit(restart_surf, restart_surf.get_rect(center=(cx, screen_h // 2 + 80)))


def draw_common_ui(surface, game_manager, cam_width, cam_height, life_display: LifeDisplay):
    """共通の UI（ライフやスコア）を描画する"""
    # ライフ表示（左上）
    try:
        life_display.draw(game_manager.lives)
    except Exception:
        # 失敗しても落とさない
        pass

    # 右上にスコアを表示
    draw_text(surface, f"Score: {game_manager.score}", (cam_width + 10, 60))

