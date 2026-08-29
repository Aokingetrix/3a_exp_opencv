"""Title, instructions, mapping, countdown, and name-selection screens."""

import pygame

from ...core import settings
from ...core.utils import render_image
from .common import draw_back_hint as _draw_back_hint


def _countdown_number(remaining_ms):
    if remaining_ms > 2000:
        return 3
    if remaining_ms > 1000:
        return 2
    if remaining_ms > 0:
        return 1
    return 0


def draw_title_screen(surface, background_surface, floating_images):
    surface.blit(background_surface, (0, 0))
    for img in floating_images:
        img.update()
        img.draw(surface)

    SCREEN_WIDTH = surface.get_width()
    SCREEN_HEIGHT = surface.get_height()

    font_l = settings.get_font(70)
    font_m = settings.get_font(40)

    title_text_surf = font_l.render(
        settings.theme_text("title", "あまのじゃくゲーム"), True, settings.TEXT_DARK
    )
    start_text_surf = font_m.render(
        settings.theme_text("start", "[S] スタート!"), True, settings.TEXT_DARK
    )

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
        pygame.draw.rect(
            box_surf, settings.WII_SHADOW_COLOR, shadow_rect, border_radius=border_radius
        )
        pygame.draw.rect(
            box_surf, settings.WII_TRANSLUCENT_BG, main_rect, border_radius=border_radius
        )
    except TypeError:
        pygame.draw.rect(box_surf, settings.WII_SHADOW_COLOR, shadow_rect)
        pygame.draw.rect(box_surf, settings.WII_TRANSLUCENT_BG, main_rect)

    title_rect = title_text_surf.get_rect(centerx=box_width // 2, top=padding)
    box_surf.blit(title_text_surf, title_rect)

    start_rect = start_text_surf.get_rect(
        centerx=box_width // 2, top=title_text_surf.get_height() + (padding * 2)
    )
    box_surf.blit(start_text_surf, start_rect)

    box_final_x = (SCREEN_WIDTH - box_total_w) // 2
    box_final_y = (SCREEN_HEIGHT - box_total_h) // 2
    surface.blit(box_surf, (box_final_x, box_final_y))

    return pygame.Rect(box_final_x, box_final_y, box_total_w, box_total_h)


def draw_skip_selection_screen(surface, background_surface, screen_w, screen_h):
    surface.blit(background_surface, (0, 0))

    font_l = settings.get_font(60)
    font_m = settings.get_font(40)

    title_text = settings.theme_text("skip_question", "遊び方の説明を見ますか？")
    yes_text = settings.theme_text("skip_yes", "[S] はい")
    no_text = settings.theme_text("skip_no", "[E] スキップ")

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
        pygame.draw.rect(
            box_surf,
            settings.WII_SHADOW_COLOR,
            (shadow_offset, shadow_offset, box_w, box_h),
            border_radius=border_radius,
        )
        pygame.draw.rect(
            box_surf, settings.WII_TRANSLUCENT_BG, (0, 0, box_w, box_h), border_radius=border_radius
        )
    except TypeError:
        pygame.draw.rect(
            box_surf, settings.WII_SHADOW_COLOR, (shadow_offset, shadow_offset, box_w, box_h)
        )
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
    _draw_back_hint(surface, left=20, bottom=18, size=22)


def draw_emotion_map_screen(surface, background_surface, game_manager, screen_w, screen_h):
    surface.blit(background_surface, (0, 0))

    font_l = settings.get_font(46)
    font_m = settings.get_font(30)
    font_s = settings.get_font(22)

    left_panel = pygame.Rect(40, 110, 560, 320)
    right_panel = pygame.Rect(680, 110, 560, 320)

    try:
        pygame.draw.rect(surface, settings.WII_TRANSLUCENT_BG, left_panel, border_radius=20)
        pygame.draw.rect(surface, settings.WII_TRANSLUCENT_BG, right_panel, border_radius=20)
    except TypeError:
        pygame.draw.rect(surface, settings.WII_TRANSLUCENT_BG, left_panel)
        pygame.draw.rect(surface, settings.WII_TRANSLUCENT_BG, right_panel)

    title_surf = font_l.render(
        settings.theme_text("emotion_map_title", "対応関係"), True, settings.TEXT_DARK
    )
    surface.blit(title_surf, title_surf.get_rect(center=(640, 45)))

    desc_surf = font_m.render(
        settings.theme_text(
            "emotion_map_description", "左のあまのじゃくの表情と、右の人間の顔が対応するよ"
        ),
        True,
        settings.TEXT_DARK,
    )
    surface.blit(desc_surf, desc_surf.get_rect(center=(640, 90)))

    npc_emotions_data = [
        ("ニコニコ", pygame.Rect(280, 130, 80, 80)),
        ("シクシク", pygame.Rect(375, 199, 80, 80)),
        ("ムカムカ", pygame.Rect(339, 311, 80, 80)),
        ("ビックリ", pygame.Rect(221, 311, 80, 80)),
        ("シーン", pygame.Rect(185, 199, 80, 80)),
    ]

    for emotion, rect in npc_emotions_data:
        try:
            emotion_img_path = game_manager.emotion_images.get(
                emotion, settings.QUESTION_IMAGE_PATH
            )
            render_image(surface, emotion_img_path, rect.x, rect.y, rect.w, rect.h, fill_bg=False)
        except Exception:
            pygame.draw.rect(surface, (0, 0, 0), rect)

        label_surf = font_s.render(emotion, True, settings.ACCENT_BLUE)
        surface.blit(label_surf, label_surf.get_rect(centerx=rect.centerx, top=rect.bottom + 4))

    human_emotions_data = [
        ("ニコニコ", pygame.Rect(920, 130, 80, 80)),
        ("シクシク", pygame.Rect(1015, 199, 80, 80)),
        ("ムカムカ", pygame.Rect(979, 311, 80, 80)),
        ("ビックリ", pygame.Rect(861, 311, 80, 80)),
        ("シーン", pygame.Rect(825, 199, 80, 80)),
    ]

    human_emotion_images = {
        "ニコニコ": getattr(settings, "HUMAN_HAPPY_PATH", settings.HUMAN_FACE_IMAGE_PATH),
        "シクシク": getattr(settings, "HUMAN_CRY_PATH", settings.HUMAN_FACE_IMAGE_PATH),
        "ムカムカ": getattr(settings, "HUMAN_ANGRY_PATH", settings.HUMAN_FACE_IMAGE_PATH),
        "ビックリ": getattr(settings, "HUMAN_SURPRISE_PATH", settings.HUMAN_FACE_IMAGE_PATH),
        "シーン": getattr(settings, "HUMAN_NO_EXP_PATH", settings.HUMAN_FACE_IMAGE_PATH),
    }

    for emotion, rect in human_emotions_data:
        try:
            img_path = human_emotion_images.get(emotion, settings.HUMAN_FACE_IMAGE_PATH)
            render_image(surface, img_path, rect.x, rect.y, rect.w, rect.h, fill_bg=False)
        except Exception:
            pygame.draw.rect(surface, (0, 0, 0), rect)

        label_surf = font_s.render(emotion, True, settings.ACCENT_RED)
        surface.blit(label_surf, label_surf.get_rect(centerx=rect.centerx, top=rect.bottom + 4))

    next_text = font_m.render("[S] 名前選択へ", True, settings.TEXT_DARK)
    surface.blit(next_text, next_text.get_rect(center=(640, 455)))


def draw_countdown_screen(surface, background_surface, game_manager, screen_w, screen_h):
    surface.blit(background_surface, (0, 0))

    font_huge = settings.get_font(180)

    remaining_ms = game_manager.countdown_remaining_ms

    count = _countdown_number(remaining_ms)

    if count > 0:
        count_surf = font_huge.render(str(count), True, settings.ACCENT_BLUE)
        surface.blit(
            count_surf,
            (
                screen_w // 2 - count_surf.get_width() // 2,
                screen_h // 2 - count_surf.get_height() // 2,
            ),
        )
    else:
        font_large = settings.get_font(80)
        ready_surf = font_large.render(
            settings.theme_text("countdown_start", "スタート！"), True, settings.ACCENT_GREEN
        )
        surface.blit(
            ready_surf,
            (
                screen_w // 2 - ready_surf.get_width() // 2,
                screen_h // 2 - ready_surf.get_height() // 2,
            ),
        )


def draw_instruction_screen(surface, background_surface, screen_w, screen_h):
    surface.blit(background_surface, (0, 0))

    char_w = 200
    char_h = 200
    char_x = screen_w - char_w - 30
    char_y = screen_h - char_h - 30

    try:
        render_image(
            surface, settings.NO_EXP_IMAGE_PATH, char_x, char_y, char_w, char_h, fill_bg=False
        )
    except Exception:
        pygame.draw.rect(surface, (255, 0, 0), (char_x, char_y, char_w, char_h))

    font_m = settings.get_font(20)
    font_s = settings.get_font(35)

    default_lines = [
        "こんにちは。わたしは「あまのじゃく」のこども。",
        " 立派な「あまのじゃく」になるため、日々奮闘中。",
        "そこのあなた、「あまのじゃく」の見本を教えてくれない？",
        "わたしの顔（ニコニコ、ムカムカ、シクシク、ビックリ）と、ちがう顔をするの。",
        "「シーン（無感情）」や、「顔が映らない」と、",
        "ライフが減っちゃうから気をつけて！",
    ]
    lines_text = settings.theme_text("instruction_lines", default_lines)

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
        pygame.draw.rect(
            box_surf, settings.WII_SHADOW_COLOR, shadow_rect, border_radius=border_radius
        )
        pygame.draw.rect(
            box_surf, settings.WII_TRANSLUCENT_BG, main_rect, border_radius=border_radius
        )
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
    _draw_back_hint(surface, left=20, bottom=18, size=22)


def draw_name_select_screen(surface, background_surface, selector, screen_w, screen_h):
    surface.blit(background_surface, (0, 0))

    font_l = settings.get_font(60)
    font_m = settings.get_font(28)
    font_s = settings.get_font(22)

    main_panel_rect = pygame.Rect(60, 80, 1160, 320)
    try:
        panel_surf = pygame.Surface((main_panel_rect.w, main_panel_rect.h), flags=pygame.SRCALPHA)
        pygame.draw.rect(
            panel_surf, settings.WII_TRANSLUCENT_BG, panel_surf.get_rect(), border_radius=12
        )
        surface.blit(panel_surf, (main_panel_rect.x, main_panel_rect.y))
    except Exception:
        pygame.draw.rect(surface, settings.WII_TRANSLUCENT_BG, main_panel_rect, border_radius=12)

    title = font_l.render(
        settings.theme_text("name_select_title", "プレイヤー名を選択"), True, settings.TEXT_DARK
    )
    surface.blit(title, (293.5, 97.0))

    hint = font_s.render(
        "↑↓: 過去名を選択 / →: 入力ウィンドウ / Enter: 決定", True, settings.TEXT_DARK
    )
    surface.blit(hint, (349.1, 411.5))

    list_rect = pygame.Rect(80, 196, 550, 180)
    input_rect = pygame.Rect(650.0, 195.0, 550, 180)

    try:
        pygame.draw.rect(surface, settings.UI_LABEL_BG, list_rect, border_radius=12)
        pygame.draw.rect(surface, settings.UI_LABEL_BG, input_rect, border_radius=12)
    except TypeError:
        pygame.draw.rect(surface, settings.UI_LABEL_BG, list_rect)
        pygame.draw.rect(surface, settings.UI_LABEL_BG, input_rect)

    if getattr(selector, "input_mode", False):
        pygame.draw.rect(surface, settings.ACCENT_BLUE, input_rect, 3, border_radius=12)
    else:
        pygame.draw.rect(surface, settings.ACCENT_BLUE, list_rect, 3, border_radius=12)

    list_title = font_s.render("過去の名前", True, settings.TEXT_DARK)
    input_title = font_s.render("新しい名前入力", True, settings.TEXT_DARK)
    surface.blit(list_title, (90, 204))
    surface.blit(input_title, (660, 204))

    recent = selector.recent or []
    recent_start_x = 110
    recent_start_y = 248
    col_width = 240
    line_spacing = 36

    for i, name in enumerate(recent[:6]):
        col = i // 3
        row = i % 3
        x = recent_start_x + (col * col_width)
        y = recent_start_y + (row * line_spacing)

        prefix = (
            "> "
            if (not getattr(selector, "input_mode", False) and selector.selected_index == i)
            else "  "
        )
        txt = font_m.render(f"{prefix}{name}", True, settings.TEXT_DARK)
        surface.blit(txt, (x, y))

    input_font = settings.get_font(28)
    input_text = selector.name or ""

    input_surf = input_font.render(input_text, True, settings.TEXT_DARK)
    surface.blit(input_surf, (662, 252))

    if getattr(selector, "input_mode", False):
        text_before_cursor = input_text[: selector.cursor_pos]
        cursor_x = 662 + input_font.size(text_before_cursor)[0]
        cursor_y = 252

        editing_text = getattr(selector, "editing_text", "")
        if editing_text:
            editing_surf = input_font.render(editing_text, True, settings.TEXT_DARK)
            surface.blit(editing_surf, (cursor_x, cursor_y))
            pygame.draw.line(
                surface,
                settings.TEXT_DARK,
                (cursor_x, cursor_y + editing_surf.get_height()),
                (cursor_x + editing_surf.get_width(), cursor_y + editing_surf.get_height()),
                2,
            )
            cursor_x += editing_surf.get_width()

        if pygame.time.get_ticks() % 1000 < 500:
            pygame.draw.line(
                surface,
                settings.TEXT_DARK,
                (cursor_x, cursor_y),
                (cursor_x, cursor_y + input_font.get_height()),
                2,
            )
