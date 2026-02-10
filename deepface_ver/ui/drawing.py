import pygame
from ..core.utils import draw_text, render_image, render_frame
from .ui_elements import LifeDisplay
from ..core import settings
from ..core.game_manager import GameState

def draw_title_screen(surface, background_surface, floating_images):
    surface.blit(background_surface, (0, 0))
    for img in floating_images:
        img.update()
        img.draw(surface)
    SCREEN_WIDTH = surface.get_width()
    SCREEN_HEIGHT = surface.get_height()
    try:
        font_l = pygame.font.Font(settings.FONT_PATH, 70)
        font_m = pygame.font.Font(settings.FONT_PATH, 40)
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

# (rest of drawing functions kept as-is, omitted here for brevity)
