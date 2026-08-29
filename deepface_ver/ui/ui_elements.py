import random

import pygame

from ..core.utils import render_image


class FloatingImage:
    def __init__(self, image_path, screen_w, screen_h):
        self.image_path = image_path
        self.screen_w = screen_w
        self.screen_h = screen_h
        base_size = screen_w // 9
        size_variation = screen_w // 18
        self.size = int(base_size + random.uniform(-size_variation, size_variation))
        self.w = self.size
        self.h = self.size
        self.x = random.uniform(0, screen_w - self.w)
        self.y = random.uniform(0, screen_h - self.h)
        self.vx = random.uniform(-1.0, 1.0)
        self.vy = random.uniform(-0.5, 0.5)
        if -0.2 < self.vx < 0.2:
            self.vx = 0.5 * random.choice([-1, 1])
        if -0.2 < self.vy < 0.2:
            self.vy = 0.3 * random.choice([-1, 1])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.x <= 0:
            self.vx = abs(self.vx)
            self.x = 0
        elif self.x + self.w >= self.screen_w:
            self.vx = -abs(self.vx)
            self.x = self.screen_w - self.w
        if self.y <= 0:
            self.vy = abs(self.vy)
            self.y = 0
        elif self.y + self.h >= self.screen_h:
            self.vy = -abs(self.vy)
            self.y = self.screen_h - self.h

    def draw(self, surface):
        render_image(
            surface, self.image_path, int(self.x), int(self.y), self.w, self.h, fill_bg=False
        )


class Timer:
    def __init__(
        self,
        screen_surface,
        pos,
        icon_path,
        font_path,
        font_size,
        text_color,
        bg_color,
        shadow_color,
    ):
        self.screen = screen_surface
        self.pos = pos
        self.text_color = text_color
        self.bg_color = bg_color
        self.shadow_color = shadow_color
        self.padding = 8
        self.icon_gap = 10
        self.shadow_offset = 3
        self.icon_height = font_size
        try:
            icon_surf_raw = pygame.image.load(icon_path)
            aspect_ratio = icon_surf_raw.get_width() / icon_surf_raw.get_height()
            self.icon_width = int(self.icon_height * aspect_ratio)
            self.icon_surface = pygame.transform.scale(
                icon_surf_raw, (self.icon_width, self.icon_height)
            )
        except Exception as e:
            print(f"タイマーアイコンの読み込みエラー: {e} (パス: {icon_path})")
            self.icon_surface = None
            self.icon_width = 0
        try:
            self.font = pygame.font.Font(font_path, font_size)
        except OSError:
            print(f"警告: タイマー用フォント '{font_path}' が見つかりません。")
            print("デフォルトフォントを使用します。")
            self.font = pygame.font.Font(None, font_size + 4)
        except Exception as e:
            print(f"タイマーフォントエラー: {e}")
            self.font = pygame.font.Font(None, font_size + 4)
        self.text_surface = self.font.render("0.0", True, self.text_color)

    def update(self, remaining_seconds):
        text = f"{remaining_seconds:.1f}"
        self.text_surface = self.font.render(text, True, self.text_color)

    def draw(self):
        text_width = self.text_surface.get_width()
        text_height = self.text_surface.get_height()
        total_width = self.padding + self.icon_width + self.icon_gap + text_width + self.padding
        total_height = max(self.icon_height, text_height) + (self.padding * 2)
        surface_width = total_width + self.shadow_offset
        surface_height = total_height + self.shadow_offset
        try:
            bg_surface = pygame.Surface((surface_width, surface_height), flags=pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 0))
        except ValueError as e:
            print(f"Pygameエラー: Surface作成失敗。 {e}")
            return
        border_radius = total_height // 2
        shadow_rect = pygame.Rect(self.shadow_offset, self.shadow_offset, total_width, total_height)
        try:
            pygame.draw.rect(
                bg_surface, self.shadow_color, shadow_rect, border_radius=border_radius
            )
        except TypeError:
            pygame.draw.rect(bg_surface, self.shadow_color, shadow_rect)
        main_rect = pygame.Rect(0, 0, total_width, total_height)
        try:
            pygame.draw.rect(bg_surface, self.bg_color, main_rect, border_radius=border_radius)
        except TypeError:
            pygame.draw.rect(bg_surface, self.bg_color, main_rect)
        icon_x = self.padding
        icon_y = (total_height - self.icon_height) // 2
        if self.icon_surface:
            bg_surface.blit(self.icon_surface, (icon_x, icon_y))
        text_x = self.padding + self.icon_width + self.icon_gap
        text_y = (total_height - text_height) // 2
        bg_surface.blit(self.text_surface, (text_x, text_y))
        self.screen.blit(bg_surface, self.pos)


class LifeDisplay:
    def __init__(self, screen_surface, icon_path, icon_size, pos, max_lives=3, spacing=5):
        self.screen = screen_surface
        self.pos = pos
        self.spacing = spacing
        self.icon_size = icon_size
        try:
            icon_surf_raw = pygame.image.load(icon_path)
            self.icon_surface = pygame.transform.scale(icon_surf_raw, (icon_size, icon_size))
        except Exception as e:
            print(f"ライフアイコンの読み込みエラー: {e} (パス: {icon_path})")
            self.icon_surface = pygame.Surface((icon_size, icon_size))
            self.icon_surface.fill((255, 0, 0))
        self.empty_icon_surface = self.icon_surface.copy()
        self.empty_icon_surface.fill((50, 50, 50), special_flags=pygame.BLEND_RGBA_MULT)
        self.max_lives = max_lives

    def draw(self, current_lives):
        draw_x = self.pos[0]
        draw_y = self.pos[1]
        for i in range(self.max_lives):
            if i < current_lives:
                self.screen.blit(self.icon_surface, (draw_x, draw_y))
            else:
                self.screen.blit(self.empty_icon_surface, (draw_x, draw_y))
            draw_x += self.icon_size + self.spacing
