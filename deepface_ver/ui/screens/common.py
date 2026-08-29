"""Shared drawing helpers."""

import pygame

from ...core import settings


def draw_text_chip(
    surface,
    text: str,
    top: int,
    right: int | None = None,
    left: int | None = None,
    size: int = 24,
    text_color=None,
    bg_color=None,
    chip_width: int | None = None,
    chip_height: int | None = None,
    use_spine_font: bool = False,
):
    if text_color is None:
        text_color = settings.TEXT_DARK
    if bg_color is None:
        bg_color = settings.UI_LABEL_BG

    current_size = size
    font = settings.get_font(current_size, use_spine_font)
    text_surf = font.render(text, True, text_color)

    if chip_width is not None and chip_height is not None:
        while (
            text_surf.get_width() > chip_width - 24 or text_surf.get_height() > chip_height - 12
        ) and current_size > 12:
            current_size -= 1
            font = settings.get_font(current_size, use_spine_font)
            text_surf = font.render(text, True, text_color)

    text_rect = text_surf.get_rect()

    if chip_width is not None and chip_height is not None:
        x = left if left is not None else (right - chip_width)
        chip_rect = pygame.Rect(x, top, chip_width, chip_height)
        text_rect.center = chip_rect.center
    else:
        padding_x = 12
        padding_y = 8
        if left is not None:
            text_rect.topleft = (left + padding_x, top + padding_y)
        else:
            text_rect.topright = (right - padding_x, top + padding_y)
        chip_rect = text_rect.inflate(padding_x * 2, padding_y * 2)

    try:
        pygame.draw.rect(surface, bg_color, chip_rect, border_radius=12)
    except TypeError:
        pygame.draw.rect(surface, bg_color, chip_rect)

    surface.blit(text_surf, text_rect)
    return chip_rect


def draw_back_hint(surface, text="[ESC] 戻る", left=20, bottom=18, size=22, color=None):
    if color is None:
        color = settings.TEXT_DARK

    font = settings.get_font(size)
    hint_surf = font.render(text, True, color)
    hint_rect = hint_surf.get_rect()
    hint_rect.left = left
    hint_rect.bottom = surface.get_height() - bottom
    surface.blit(hint_surf, hint_rect)
    return hint_rect
