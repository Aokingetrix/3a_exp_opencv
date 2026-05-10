import pygame
from typing import Optional
from ..core.utils import draw_text, render_image, render_frame
from .ui_elements import LifeDisplay
from ..core import settings
from ..core.game_manager import GameState
from ..core import highscore
from .name_select import NameSelector


def _draw_text_chip(
    surface,
    text: str,
    right: int,
    top: int,
    size: int = 24,
    text_color=None,
    bg_color=None,
    chip_width: Optional[int] = None,
    chip_height: Optional[int] = None,
):
    if text_color is None:
        text_color = settings.TEXT_DARK
    if bg_color is None:
        bg_color = settings.UI_LABEL_BG

    current_size = size
    while current_size >= 14:
        try:
            font = pygame.font.Font(settings.FONT_PATH, current_size)
        except Exception:
            font = pygame.font.Font(None, current_size + 4)
        text_surf = font.render(text, True, text_color)

        if chip_width is None or chip_height is None:
            break

        if text_surf.get_width() <= chip_width - 24 and text_surf.get_height() <= chip_height - 12:
            break
        current_size -= 1

    text_rect = text_surf.get_rect()

    if chip_width is not None and chip_height is not None:
        chip_rect = pygame.Rect(right - chip_width, top, chip_width, chip_height)
        text_rect.center = chip_rect.center
    else:
        text_rect.top = top
        text_rect.right = right - 12
        padding_x = 12
        padding_y = 8
        chip_rect = pygame.Rect(
            text_rect.left - padding_x,
            text_rect.top - padding_y,
            text_rect.width + padding_x * 2,
            text_rect.height + padding_y * 2,
        )

    try:
        pygame.draw.rect(surface, bg_color, chip_rect, border_radius=12)
    except TypeError:
        pygame.draw.rect(surface, bg_color, chip_rect)

    surface.blit(text_surf, text_rect)
    return chip_rect


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
    title_box_rect = pygame.Rect(box_final_x, box_final_y, box_total_w, box_total_h)

    return title_box_rect


def draw_skip_selection_screen(surface, background_surface, screen_w, screen_h):
    """説明スキップ選択画面を描画する"""
    surface.blit(background_surface, (0, 0))
    
    try:
        font_l = pygame.font.Font(settings.FONT_PATH, 60)
        font_m = pygame.font.Font(settings.FONT_PATH, 40)
    except Exception:
        font_l = pygame.font.Font(None, 64)
        font_m = pygame.font.Font(None, 44)
    
    title_text = "遊び方の説明を見ますか？"
    yes_text = "[S] はい"
    no_text = "[E] スキップ"
    
    title_surf = font_l.render(title_text, True, settings.TEXT_DARK)
    yes_surf = font_m.render(yes_text, True, settings.ACCENT_BLUE)
    no_surf = font_m.render(no_text, True, settings.ACCENT_RED)
    
    padding = 20
    shadow_offset = 5
    
    box_w = max(title_surf.get_width(), yes_surf.get_width(), no_surf.get_width()) + (padding * 2)
    box_h = title_surf.get_height() + yes_surf.get_height() + no_surf.get_height() + (padding * 4)
    
    box_total_w = box_w + shadow_offset
    box_total_h = box_h + shadow_offset
    box_surf = pygame.Surface((box_total_w, box_total_h), flags=pygame.SRCALPHA)
    
    border_radius = 20
    try:
        pygame.draw.rect(box_surf, settings.WII_SHADOW_COLOR, (shadow_offset, shadow_offset, box_w, box_h), border_radius=border_radius)
        pygame.draw.rect(box_surf, settings.WII_TRANSLUCENT_BG, (0, 0, box_w, box_h), border_radius=border_radius)
    except TypeError:
        pygame.draw.rect(box_surf, settings.WII_SHADOW_COLOR, (shadow_offset, shadow_offset, box_w, box_h))
        pygame.draw.rect(box_surf, settings.WII_TRANSLUCENT_BG, (0, 0, box_w, box_h))
    
    y_pos = padding
    box_surf.blit(title_surf, (padding, y_pos))
    y_pos += title_surf.get_height() + padding
    box_surf.blit(yes_surf, (padding, y_pos))
    y_pos += yes_surf.get_height() + padding
    box_surf.blit(no_surf, (padding, y_pos))
    
    box_x = (screen_w - box_total_w) // 2
    box_y = (screen_h - box_total_h) // 2
    surface.blit(box_surf, (box_x, box_y))


def draw_emotion_map_screen(surface, background_surface, game_manager, screen_w, screen_h):
    """感情対応関係明示画面を描画する"""
    surface.blit(background_surface, (0, 0))
    
    try:
        font_l = pygame.font.Font(settings.FONT_PATH, 46)
        font_m = pygame.font.Font(settings.FONT_PATH, 30)
        font_s = pygame.font.Font(settings.FONT_PATH, 22)
    except Exception:
        font_l = pygame.font.Font(None, 50)
        font_m = pygame.font.Font(None, 34)
        font_s = pygame.font.Font(None, 26)
    
    title_surf = font_l.render("対応関係", True, settings.TEXT_DARK)
    desc_surf = font_m.render("左のあまのじゃくの表情と、右の人間の顔を対応させてね", True, settings.TEXT_DARK)

    title_y = 30
    surface.blit(title_surf, title_surf.get_rect(centerx=screen_w // 2, top=title_y))

    desc_y = title_y + title_surf.get_height() + 18
    surface.blit(desc_surf, desc_surf.get_rect(centerx=screen_w // 2, top=desc_y))

    content_top = desc_y + desc_surf.get_height() + 28
    bottom_reserved = 92
    content_bottom = screen_h - bottom_reserved
    content_h = max(240, content_bottom - content_top)

    half_w = screen_w // 2
    left_x = 40
    left_w = half_w - 60
    right_x = half_w + 20
    right_w = half_w - 60

    left_panel = pygame.Rect(left_x, content_top, left_w, content_h)
    right_panel = pygame.Rect(right_x, content_top, right_w, content_h)

    try:
        pygame.draw.rect(surface, settings.WII_TRANSLUCENT_BG, left_panel, border_radius=20)
        pygame.draw.rect(surface, settings.WII_TRANSLUCENT_BG, right_panel, border_radius=20)
    except TypeError:
        pygame.draw.rect(surface, settings.WII_TRANSLUCENT_BG, left_panel)
        pygame.draw.rect(surface, settings.WII_TRANSLUCENT_BG, right_panel)

    npc_title = font_m.render("あまのじゃく", True, settings.TEXT_DARK)
    human_title = font_m.render("あなた", True, settings.TEXT_DARK)
    surface.blit(npc_title, npc_title.get_rect(centerx=left_panel.centerx, top=left_panel.y + 14))
    surface.blit(human_title, human_title.get_rect(centerx=right_panel.centerx, top=right_panel.y + 14))

    emotion_grid_top = left_panel.y + 70
    emotion_grid_w = left_panel.w - 40
    cell_w = (emotion_grid_w - 16) // 2
    cell_h = 118
    cell_gap_x = 16
    cell_gap_y = 16

    emotion_items = [
        ("ニコニコ", settings.ACCENT_BLUE),
        ("シクシク", settings.ACCENT_BLUE),
        ("ムカムカ", settings.ACCENT_BLUE),
        ("ビックリ", settings.ACCENT_BLUE),
    ]

    for index, (emotion, color) in enumerate(emotion_items):
        row = index // 2
        col = index % 2
        cell_x = left_panel.x + 20 + col * (cell_w + cell_gap_x)
        cell_y = emotion_grid_top + row * (cell_h + cell_gap_y)
        image_box_h = 78
        image_box = pygame.Rect(cell_x, cell_y, cell_w, image_box_h)

        try:
            emotion_img_path = game_manager.emotion_images.get(emotion, settings.QUESTION_IMAGE_PATH)
            render_image(surface, emotion_img_path, image_box.x, image_box.y, image_box.w, image_box.h, fill_bg=False)
        except Exception:
            pygame.draw.rect(surface, (0, 0, 0), image_box)

        label_surf = font_s.render(emotion, True, color)
        surface.blit(label_surf, label_surf.get_rect(centerx=image_box.centerx, top=image_box.bottom + 8))

    human_box_w = right_panel.w - 80
    human_box_h = min(260, content_h - 110)
    human_box_x = right_panel.x + (right_panel.w - human_box_w) // 2
    human_box_y = right_panel.y + 74
    human_box = pygame.Rect(human_box_x, human_box_y, human_box_w, human_box_h)

    try:
        render_image(surface, settings.HUMAN_FACE_IMAGE_PATH, human_box.x, human_box.y, human_box.w, human_box.h, fill_bg=False)
    except Exception:
        pygame.draw.rect(surface, (0, 0, 0), human_box)

    human_hint = font_s.render("写真は data/ に追加", True, settings.TEXT_DARK)
    surface.blit(human_hint, human_hint.get_rect(centerx=right_panel.centerx, top=human_box.bottom + 12))

    next_text = font_m.render("[S] 名前選択へ", True, settings.TEXT_DARK)
    next_rect = next_text.get_rect(centerx=screen_w // 2, bottom=screen_h - 22)
    surface.blit(next_text, next_rect)


def draw_countdown_screen(surface, background_surface, game_manager, screen_w, screen_h):
    """3-2-1 カウントダウン画面を描画する"""
    surface.blit(background_surface, (0, 0))
    
    try:
        font_huge = pygame.font.Font(settings.FONT_PATH, 180)
    except Exception:
        font_huge = pygame.font.Font(None, 200)
    
    elapsed_ms = pygame.time.get_ticks() - game_manager.countdown_start_time
    remaining_ms = game_manager.countdown_duration_ms - elapsed_ms
    
    if remaining_ms > 2000:
        count = 3
    elif remaining_ms > 1000:
        count = 2
    elif remaining_ms > 0:
        count = 1
    else:
        count = 0
    
    if count > 0:
        count_surf = font_huge.render(str(count), True, settings.ACCENT_BLUE)
        surface.blit(count_surf, (screen_w // 2 - count_surf.get_width() // 2, screen_h // 2 - count_surf.get_height() // 2))
    else:
        # カウント終了時は準備完了メッセージ
        try:
            font_large = pygame.font.Font(settings.FONT_PATH, 80)
        except Exception:
            font_large = pygame.font.Font(None, 88)
        ready_surf = font_large.render("スタート！", True, settings.ACCENT_GREEN)
        surface.blit(ready_surf, (screen_w // 2 - ready_surf.get_width() // 2, screen_h // 2 - ready_surf.get_height() // 2))


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
        render_image(surface, settings.NO_EXP_IMAGE_PATH, char_x, char_y, char_w, char_h, fill_bg=False)
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
    right_edge = surface.get_width() - 20
    _draw_text_chip(
        surface,
        f"あなた: {smoothed_emotion}",
        right_edge,
        116,
        size=24,
        chip_width=300,
        chip_height=44,
    )


def draw_developer_screen(surface, background_surface, frame, result, cam_width):
    """開発者用の診断画面を描画する。"""
    screen_h = surface.get_height()

    surface.blit(background_surface, (0, 0))
    render_frame(surface, frame, result, cam_width, 0)
    surface.fill(settings.WII_BACKGROUND, (0, 0, cam_width, screen_h))

    status = result.get("status", "unknown") if isinstance(result, dict) else "unknown"
    reason = result.get("reason", "") if isinstance(result, dict) else ""
    top_emotion = result.get("top_emotion", "探し中...") if isinstance(result, dict) else "探し中..."
    latency_ms = result.get("latency_ms", 0.0) if isinstance(result, dict) else 0.0
    face_detected = result.get("face_detected", False) if isinstance(result, dict) else False
    emotion_success = result.get("emotion_success", False) if isinstance(result, dict) else False
    detector = result.get("detector", "-") if isinstance(result, dict) else "-"
    classifier = result.get("classifier", "-") if isinstance(result, dict) else "-"
    box = result.get("box") if isinstance(result, dict) else None

    if status == "ok":
        status_text = "OK"
        status_color = settings.ACCENT_GREEN
    elif status == "no_face":
        status_text = "顔検出失敗"
        status_color = settings.ACCENT_RED
    elif status == "emotion_error":
        status_text = "感情分類失敗"
        status_color = settings.ACCENT_RED
    else:
        status_text = status
        status_color = settings.TEXT_DARK

    y = 20
    draw_text(surface, "開発者モード", (20, y), size=36)
    y += 52
    draw_text(surface, f"状態: {status_text}", (20, y), color=status_color, size=30)
    y += 44
    draw_text(surface, f"感情: {top_emotion}", (20, y), size=28)
    y += 40
    draw_text(surface, f"顔検出: {'成功' if face_detected else '失敗'}", (20, y), size=24)
    y += 34
    draw_text(surface, f"感情分類: {'成功' if emotion_success else '失敗'}", (20, y), size=24)
    y += 34
    draw_text(surface, f"遅延: {latency_ms} ms", (20, y), size=24)
    y += 34
    draw_text(surface, f"detector: {detector}", (20, y), size=20)
    y += 30
    draw_text(surface, f"classifier: {classifier}", (20, y), size=20)
    y += 30

    if box and isinstance(box, dict):
        draw_text(surface, f"box: x={box.get('x')} y={box.get('y')} w={box.get('w')} h={box.get('h')}", (20, y), size=20)
        y += 30
    else:
        draw_text(surface, "box: None", (20, y), size=20)
        y += 30

    if reason:
        draw_text(surface, f"reason: {reason[:52]}", (20, y), size=20)

    draw_text(surface, "[R] タイトルへ戻る", (20, screen_h - 40), size=24)


def draw_name_select_screen(surface, background_surface, selector: NameSelector, screen_w, screen_h):
    surface.blit(background_surface, (0, 0))
    try:
        font_l = pygame.font.Font(settings.FONT_PATH, 60)
        font_m = pygame.font.Font(settings.FONT_PATH, 28)
        font_s = pygame.font.Font(settings.FONT_PATH, 22)
    except Exception:
        font_l = pygame.font.Font(None, 64)
        font_m = pygame.font.Font(None, 30)
        font_s = pygame.font.Font(None, 26)

    box_w = screen_w - 120
    box_h = 320
    box_x = 60
    box_y = (screen_h - box_h) // 2

    # background panel
    try:
        panel = pygame.Surface((box_w, box_h), flags=pygame.SRCALPHA)
        pygame.draw.rect(panel, settings.WII_TRANSLUCENT_BG, panel.get_rect(), border_radius=12)
    except Exception:
        panel = pygame.Surface((box_w, box_h))
        panel.fill(settings.WII_TRANSLUCENT_BG)

    surface.blit(panel, (box_x, box_y))

    title = font_l.render("プレイヤー名を選択", True, settings.TEXT_DARK)
    surface.blit(title, (box_x + 20, box_y + 14))

    hint = font_s.render("↑↓: 過去名を選択 / →: 入力ウィンドウ / Enter: 決定", True, settings.TEXT_DARK)
    surface.blit(hint, (box_x + 20, box_y + 80))

    list_rect = pygame.Rect(box_x + 20, box_y + 116, box_w // 2 - 30, 180)
    input_rect = pygame.Rect(box_x + box_w // 2 + 10, box_y + 116, box_w // 2 - 30, 180)
    try:
        pygame.draw.rect(surface, settings.UI_LABEL_BG, list_rect, border_radius=12)
        pygame.draw.rect(surface, settings.UI_LABEL_BG, input_rect, border_radius=12)
    except TypeError:
        pygame.draw.rect(surface, settings.UI_LABEL_BG, list_rect)
        pygame.draw.rect(surface, settings.UI_LABEL_BG, input_rect)

    if selector.input_mode:
        pygame.draw.rect(surface, settings.ACCENT_BLUE, input_rect, 3, border_radius=12)
    else:
        pygame.draw.rect(surface, settings.ACCENT_BLUE, list_rect, 3, border_radius=12)

    list_title = font_s.render("過去の名前", True, settings.TEXT_DARK)
    input_title = font_s.render("新しい名前入力", True, settings.TEXT_DARK)
    surface.blit(list_title, (list_rect.x + 10, list_rect.y + 8))
    surface.blit(input_title, (input_rect.x + 10, input_rect.y + 8))

    # recent list
    recent = selector.recent or []
    for i, name in enumerate(recent[:6]):
        y = list_rect.y + 44 + i * 36
        prefix = "> " if (not selector.input_mode and selector.selected_index == i) else "  "
        txt = font_m.render(f"{prefix}{name}", True, settings.TEXT_DARK)
        surface.blit(txt, (list_rect.x + 12, y))

    try:
        input_font = pygame.font.Font(settings.FONT_PATH, 28)
    except Exception:
        input_font = pygame.font.Font(None, 30)
    input_text = selector.name or ""
    input_surf = input_font.render(input_text, True, settings.TEXT_DARK)
    surface.blit(input_surf, (input_rect.x + 12, input_rect.y + 56))


def draw_best_lists(surface, screen_w, screen_h, selected_name: str, avoid_rect: Optional[pygame.Rect] = None):
    """Draw overall top10 and selected name top3 in a side panel (used on title/result)."""
    try:
        font_m = pygame.font.Font(settings.FONT_PATH, 20)
    except Exception:
        font_m = pygame.font.Font(None, 20)

    all_best = highscore.get_all_names_best(10)
    sel_best = highscore.get_best_for_name(selected_name or "名無し", n=3)

    panel_w = 320
    panel_x = screen_w - panel_w - 20
    panel_h = 356
    panel_y = (screen_h - panel_h) // 2

    panel = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

    shadow = pygame.Rect(panel.x + 4, panel.y + 4, panel_w, panel_h)
    try:
        pygame.draw.rect(surface, settings.WII_SHADOW_COLOR, shadow, border_radius=16)
        pygame.draw.rect(surface, settings.UI_PANEL_BG, panel, border_radius=16)
    except TypeError:
        pygame.draw.rect(surface, settings.WII_SHADOW_COLOR, shadow)
        pygame.draw.rect(surface, settings.UI_PANEL_BG, panel)

    draw_text(surface, "全名ベスト10", (panel.x + 16, panel.y + 14), size=18)
    for i, rec in enumerate(all_best[:10]):
        draw_text(surface, f"{i+1}. {rec['name']} {rec['score']}", (panel.x + 16, panel.y + 40 + i * 20), size=16)

    draw_text(surface, f"{selected_name} のベスト3", (panel.x + 16, panel.y + 252), size=18)
    for i, s in enumerate(sel_best[:3]):
        draw_text(surface, f"{i+1}. {s}", (panel.x + 16, panel.y + 278 + i * 20), size=16)


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
        font_s = pygame.font.Font(settings.FONT_PATH, 22)
    except Exception:
        font_m = pygame.font.Font(None, 44)
        font_l = pygame.font.Font(None, 74)
        font_s = pygame.font.Font(None, 26)

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
        npc_img_path = game_manager.emotion_images.get(game_manager.npc_emotions[0], settings.QUESTION_IMAGE_PATH)
        render_image(surface, npc_img_path, npc_area_x, npc_area_y, npc_area_w, npc_area_h, fill_bg=False)

    elif num_npcs == 2:
        half_w = npc_area_w // 2
        npc_img_path1 = game_manager.emotion_images.get(game_manager.npc_emotions[0], settings.QUESTION_IMAGE_PATH)
        render_image(surface, npc_img_path1, npc_area_x, npc_area_y, half_w, npc_area_h, fill_bg=False)
        
        npc_img_path2 = game_manager.emotion_images.get(game_manager.npc_emotions[1], settings.QUESTION_IMAGE_PATH)
        render_image(surface, npc_img_path2, npc_area_x + half_w, npc_area_y, half_w, npc_area_h, fill_bg=False)

    elif num_npcs >= 3:
        half_w = npc_area_w // 2
        half_h = npc_area_h // 2
        npc_img_path1 = game_manager.emotion_images.get(game_manager.npc_emotions[0], settings.QUESTION_IMAGE_PATH)
        render_image(surface, npc_img_path1, npc_area_x, npc_area_y, half_w, half_h, fill_bg=False)
        
        npc_img_path2 = game_manager.emotion_images.get(game_manager.npc_emotions[1], settings.QUESTION_IMAGE_PATH)
        render_image(surface, npc_img_path2, npc_area_x + half_w, npc_area_y, half_w, half_h, fill_bg=False)

        npc_img_path3 = game_manager.emotion_images.get(game_manager.npc_emotions[2], settings.QUESTION_IMAGE_PATH)
        render_image(surface, npc_img_path3, npc_area_x, npc_area_y + half_h, half_w, half_h, fill_bg=False)

        if num_npcs >= 4:
            npc_img_path4 = game_manager.emotion_images.get(game_manager.npc_emotions[3], settings.QUESTION_IMAGE_PATH)
            render_image(surface, npc_img_path4, npc_area_x + half_w, npc_area_y + half_h, half_w, half_h, fill_bg=False)

    player_area_x = panel_center_x + 40
    player_area_y = 120
    player_area_w = panel_center_x - 40
    player_area_h = 200

    player_img_path = game_manager.emotion_images.get(game_manager.player_emotion, settings.QUESTION_IMAGE_PATH)
    render_image(surface, player_img_path, player_area_x, player_area_y, player_area_w, player_area_h, fill_bg=False)

    vs_surf = font_m.render("VS", True, settings.TEXT_DARK)
    vs_rect = vs_surf.get_rect(centerx=panel_center_x, centery=npc_area_y + npc_area_h // 2)
    surface.blit(vs_surf, vs_rect)

    outcome = game_manager.last_round_outcome
    if outcome == "success":
        result_text = "成功！"
        result_color = settings.ACCENT_GREEN
    else:
        result_text = "失敗..."
        result_color = settings.ACCENT_RED

    result_surf = font_l.render(result_text, True, result_color)
    result_rect = result_surf.get_rect(centerx=panel_center_x, top=320)
    surface.blit(result_surf, result_rect)

    if game_manager.lives <= 0:
        nav_text = "[S] 最終結果へ"
    else:
        nav_text = "[S] 次のラウンドへ"

    nav_font = font_m
    nav_max_width = panel_center_x - 36
    nav_size = 40
    while nav_size >= 22:
        try:
            nav_font_try = pygame.font.Font(settings.FONT_PATH, nav_size)
        except Exception:
            nav_font_try = pygame.font.Font(None, nav_size + 4)
        nav_surf_try = nav_font_try.render(nav_text, True, settings.TEXT_DARK)
        if nav_surf_try.get_width() <= nav_max_width:
            nav_font = nav_font_try
            nav_surf = nav_surf_try
            break
        nav_size -= 1
    else:
        nav_surf = nav_font.render(nav_text, True, settings.TEXT_DARK)

    nav_rect = nav_surf.get_rect()
    nav_rect.right = cam_width - 20
    nav_rect.bottom = cam_height - 18
    surface.blit(nav_surf, nav_rect)

    bottom_margin = 16
    line_gap = 8

    score_surf = font_s.render(f"Score: {game_manager.score}", True, settings.TEXT_DARK)
    if getattr(game_manager, 'new_personal_best', False):
        best_surf = font_s.render("ベストスコア！", True, settings.ACCENT_GREEN)
        best_rect = best_surf.get_rect(centerx=panel_center_x, bottom=cam_height - bottom_margin)
        score_rect = score_surf.get_rect(centerx=panel_center_x, bottom=best_rect.top - line_gap)
        surface.blit(score_surf, score_rect)
        surface.blit(best_surf, best_rect)
    else:
        score_rect = score_surf.get_rect(centerx=panel_center_x, bottom=cam_height - bottom_margin)
        surface.blit(score_surf, score_rect)


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
    # show personal best update flag if present
    if getattr(game_manager, 'new_personal_best', False):
        try:
            font_flag = pygame.font.Font(settings.FONT_PATH, 28)
        except Exception:
            font_flag = pygame.font.Font(None, 28)
        flag_surf = font_flag.render("スコア更新中！", True, settings.ACCENT_GREEN)
        surface.blit(flag_surf, flag_surf.get_rect(center=(cx, screen_h // 2 + 120)))


def draw_common_ui(surface, game_manager, cam_width, cam_height, life_display: LifeDisplay):
    """共通の UI（ライフやスコア）を描画する"""
    # ライフ表示（左上）
    try:
        life_display.draw(game_manager.lives)
    except Exception:
        # 失敗しても落とさない
        pass

    right_edge = surface.get_width() - 20
    chip_width = 300
    chip_height = 44

    # プレイヤー名を自分の顔側（右上）に表示
    player_name = getattr(game_manager, 'player_name', '名無し')
    name_rect = _draw_text_chip(
        surface,
        f"名前: {player_name}",
        right_edge,
        12,
        size=24,
        chip_width=chip_width,
        chip_height=chip_height,
    )

    # スコア表示（背景つき）
    score_rect = _draw_text_chip(
        surface,
        f"Score: {game_manager.score}",
        right_edge,
        name_rect.bottom + 8,
        size=24,
        chip_width=chip_width,
        chip_height=chip_height,
    )

    # 新記録フラグ表示（ゲーム中も表示）
    if getattr(game_manager, 'new_personal_best', False):
        _draw_text_chip(
            surface,
            "スコア更新中！",
            cam_width + 280,
            16,
            size=22,
            text_color=settings.ACCENT_GREEN,
            chip_width=260,
            chip_height=chip_height,
        )

