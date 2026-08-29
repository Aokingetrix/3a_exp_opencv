"""High-score panels."""

import pygame

from ...core import settings
from ...core.utils import draw_text


def draw_title_highscores(surface, screen_w, best_all, best_today):
    """タイトル画面右上に歴代ベスト5と本日ベスト3を表示"""
    panel_w, panel_h = 250, 400
    panel = pygame.Rect(screen_w - panel_w - 20, 20, panel_w, panel_h)

    try:
        pygame.draw.rect(surface, settings.WII_SHADOW_COLOR, panel.move(4, 4), border_radius=16)
        pygame.draw.rect(surface, settings.UI_PANEL_BG, panel, border_radius=16)
    except TypeError:
        pygame.draw.rect(surface, settings.WII_SHADOW_COLOR, panel.move(4, 4))
        pygame.draw.rect(surface, settings.UI_PANEL_BG, panel)

    y = panel.y + 20
    draw_text(surface, "歴代ベスト5", (panel.x + 15, y), size=24, color=settings.TEXT_DARK)
    y += 35
    if not best_all:
        draw_text(surface, "データがありません", (panel.x + 25, y), size=18)
        y += 24
    else:
        for i, rec in enumerate(best_all[:5]):
            draw_text(surface, f"{i + 1}. {rec['name']} {rec['score']}", (panel.x + 25, y), size=20)
            y += 28

    y += 30
    draw_text(surface, "本日のベスト3", (panel.x + 15, y), size=24, color=settings.TEXT_DARK)
    y += 35
    if not best_today:
        draw_text(surface, "今日の記録はまだありません", (panel.x + 25, y), size=18)
    else:
        for i, rec in enumerate(best_today[:3]):
            draw_text(surface, f"{i + 1}. {rec['name']} {rec['score']}", (panel.x + 25, y), size=20)
            y += 28


def draw_finish_highscores(surface, screen_w, game_manager):
    """終了画面右上に、今回の順位と自己ベストをコンパクトにまとめて描画"""
    panel_w, panel_h = 260, 260
    panel = pygame.Rect(screen_w - panel_w - 20, 20, panel_w, panel_h)

    try:
        pygame.draw.rect(surface, settings.WII_SHADOW_COLOR, panel.move(4, 4), border_radius=12)
        pygame.draw.rect(surface, settings.UI_PANEL_BG, panel, border_radius=12)
    except TypeError:
        pygame.draw.rect(surface, settings.WII_SHADOW_COLOR, panel.move(4, 4))
        pygame.draw.rect(surface, settings.UI_PANEL_BG, panel)

    y = panel.y + 12
    draw_text(surface, "今回の順位", (panel.x + 12, y), size=18, color=settings.TEXT_DARK)
    y += 32

    t_rank = getattr(game_manager, "todays_rank", 0)
    a_rank = getattr(game_manager, "all_time_rank", 0)

    draw_text(
        surface, f"本日: {t_rank}位！", (panel.x + 20, y), size=22, color=settings.ACCENT_GREEN
    )
    y += 30
    draw_text(surface, f"歴代: {a_rank}位！", (panel.x + 20, y), size=18)

    y += 40
    p_name = getattr(game_manager, "player_name", "名無し")
    draw_text(surface, f"{p_name}のベスト3", (panel.x + 12, y), size=18, color=settings.TEXT_DARK)
    y += 28

    best_list = getattr(game_manager, "personal_best_list", [])
    if not best_list:
        draw_text(surface, "なし", (panel.x + 20, y), size=16)
    else:
        for i, s in enumerate(best_list[:3]):
            draw_text(surface, f"{i + 1}. {s}点", (panel.x + 20, y), size=16)
            y += 22
